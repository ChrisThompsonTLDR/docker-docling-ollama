#!/usr/bin/env python3
"""
Docling PDF extraction via PdfPipeline + RapidOCR + Ollama picture description.
Converts PDF to DoclingDocument, exports to JSON and Markdown.
Extracts figures and tables as images. Sends pictures to Ollama for VLM alt-text.
"""
from __future__ import annotations

import os
from pathlib import Path

from docling.document_converter import DocumentConverter


def _make_converter(output_dir: str | None) -> DocumentConverter:
    """Build DocumentConverter with PdfPipeline + RapidOCR + Ollama picture description."""
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import (
        PdfPipelineOptions,
        PictureDescriptionApiOptions,
        RapidOcrOptions,
    )
    from docling.document_converter import PdfFormatOption

    do_picture_desc = os.environ.get("DOCLING_OLLAMA_DO_PICTURE_DESCRIPTION", "true").lower() not in (
        "false",
        "0",
        "no",
    )
    ollama_url = (os.environ.get("DOCLING_OLLAMA_BASE_URL") or "http://ollama:11434").rstrip("/")
    ollama_api_key = os.environ.get("DOCLING_OLLAMA_API_KEY", "")
    model = os.environ.get("DOCLING_OLLAMA_MODEL", "qwen3.5:397b-cloud")
    images_scale = float(os.environ.get("DOCLING_OLLAMA_IMAGES_SCALE", "2.0"))

    pipeline_options = PdfPipelineOptions()
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True
    pipeline_options.images_scale = images_scale
    pipeline_options.ocr_options = RapidOcrOptions()

    if do_picture_desc and ollama_url:
        pipeline_options.do_picture_description = True
        pipeline_options.enable_remote_services = True
        api_url = f"{ollama_url}/v1/chat/completions"
        headers = {}
        if ollama_api_key:
            headers["Authorization"] = f"Bearer {ollama_api_key}"
        pipeline_options.picture_description_options = PictureDescriptionApiOptions(
            url=api_url,
            headers=headers,
            params={"model": model},
            prompt=(
                "Provide a dense, factual description of the image capturing all key "
                "visual elements for retrieval. If the image contains code, source code, "
                "or terminal output, transcribe it exactly preserving formatting for retrieval."
            ),
            timeout=120,
            concurrency=4,
            picture_area_threshold=0.0,
        )

    return DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    )


def _get_alt_text(element, result) -> str | None:
    """Extract VLM-generated description from PictureItem or TableItem."""
    if hasattr(element, "meta") and element.meta is not None:
        if hasattr(element.meta, "description") and element.meta.description is not None:
            if hasattr(element.meta.description, "text"):
                return element.meta.description.text or None
    if hasattr(element, "annotations") and element.annotations:
        for ann in element.annotations:
            if hasattr(ann, "text") and ann.text:
                return ann.text
    if hasattr(element, "caption_text"):
        try:
            cap = element.caption_text(doc=result.document)
            if cap and cap.strip():
                return cap.strip()
        except Exception:
            pass
    return None


def extract(pdf_path: str, output_dir: str | None = None) -> dict:
    """
    Convert PDF to DoclingDocument; export to JSON and Markdown.
    When output_dir is provided, extracts figures and tables as images
    with VLM-generated alt-text via Ollama.

    Returns dict with docling_document, docling_markdown, and docling_images.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    generate_images = output_dir is not None
    converter = _make_converter(output_dir)
    result = converter.convert(str(pdf_path))

    if not result.document:
        raise RuntimeError(f"Docling conversion failed for {pdf_path}")

    doc = result.document
    docling_document = doc.export_to_dict() if hasattr(doc, "export_to_dict") else doc.model_dump()

    docling_images = []

    if generate_images and output_dir:
        from docling_core.types.doc import ImageRefMode, PictureItem, TableItem

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        images_dir = output_path / "images"
        images_dir.mkdir(exist_ok=True)

        picture_counters = {}
        table_counters = {}

        for element, _level in doc.iterate_items():
            page_no = None
            if hasattr(element, "prov") and element.prov:
                page_no = element.prov[0].page_no

            if isinstance(element, PictureItem):
                if page_no is None:
                    continue
                picture_counters[page_no] = picture_counters.get(page_no, 0) + 1
                idx = picture_counters[page_no]
                rel_path = f"images/page{page_no}_picture_{idx}.png"
                abs_path = output_path / rel_path

                try:
                    img = element.get_image(result.document)
                    if img:
                        abs_path.parent.mkdir(parents=True, exist_ok=True)
                        img.save(str(abs_path), "PNG")
                        if hasattr(element, "image") and element.image is not None:
                            element.image.uri = rel_path
                        alt_text = _get_alt_text(element, result)
                        docling_images.append(
                            {
                                "page_number": page_no,
                                "path": rel_path,
                                "element_type": "picture",
                                "element_index": idx,
                                "alt_text": alt_text,
                            }
                        )
                except Exception:
                    pass

            elif isinstance(element, TableItem):
                if page_no is None:
                    continue
                table_counters[page_no] = table_counters.get(page_no, 0) + 1
                idx = table_counters[page_no]
                rel_path = f"images/page{page_no}_table_{idx}.png"
                abs_path = output_path / rel_path

                try:
                    img = element.get_image(result.document)
                    if img:
                        abs_path.parent.mkdir(parents=True, exist_ok=True)
                        img.save(str(abs_path), "PNG")
                        if hasattr(element, "image") and element.image is not None:
                            element.image.uri = rel_path
                        alt_text = _get_alt_text(element, result)
                        docling_images.append(
                            {
                                "page_number": page_no,
                                "path": rel_path,
                                "element_type": "table",
                                "element_index": idx,
                                "alt_text": alt_text,
                            }
                        )
                except Exception:
                    pass

        md_path = output_path / f"{pdf_path.stem}.md"
        try:
            doc.save_as_markdown(str(md_path), image_mode=ImageRefMode.REFERENCED)
            docling_markdown = md_path.read_text(encoding="utf-8")
        except Exception:
            docling_markdown = doc.export_to_markdown()
    else:
        docling_markdown = doc.export_to_markdown()

    return {
        "docling_document": docling_document,
        "docling_markdown": docling_markdown,
        "docling_images": docling_images,
    }
