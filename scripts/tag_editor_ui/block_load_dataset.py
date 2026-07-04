from __future__ import annotations
from typing import TYPE_CHECKING, List, Callable
import gradio as gr

from modules import shared
from modules.shared import opts

from .ui_common import *
from .uibase import UIBase

if TYPE_CHECKING:
    from .ui_classes import *


class LoadDatasetUI(UIBase):
    def __init__(self):
        self.caption_file_ext = ""

    def create_ui(self, cfg_general):
        with gr.Column(variant="panel"):
            with gr.Row():
                with gr.Column(scale=3):
                    self.tb_img_directory = gr.Textbox(
                        label="Dataset directory",
                        placeholder="C:\\directory\\of\\datasets",
                        value=cfg_general.dataset_dir,
                    )
                with gr.Column(scale=1, min_width=60):
                    self.tb_caption_file_ext = gr.Textbox(
                        label="Caption File Ext",
                        placeholder=".txt (on Load and Save)",
                        value=cfg_general.caption_ext,
                    )
                    self.caption_file_ext = cfg_general.caption_ext
                with gr.Column(scale=1, min_width=80):
                    self.btn_load_datasets = gr.Button(value="Load")
                    self.btn_unload_datasets = gr.Button(value="Unload")
            with gr.Accordion(label="Dataset Load Settings"):
                with gr.Row():
                    with gr.Column():
                        self.cb_load_recursive = gr.Checkbox(
                            value=cfg_general.load_recursive,
                            label="Load from subdirectories",
                        )
                        self.cb_load_caption_from_filename = gr.Checkbox(
                            value=cfg_general.load_caption_from_filename,
                            label="Load caption from filename if no text file exists",
                        )
                        self.cb_replace_new_line_with_comma = gr.Checkbox(
                            value=cfg_general.replace_new_line,
                            label="Replace new-line character with comma",
                        )

    def set_callbacks(
        self,
        o_update_filter_and_gallery: List[gr.components.Component],
        toprow: ToprowUI,
        dataset_gallery: DatasetGalleryUI,
        filter_by_tags: FilterByTagsUI,
        filter_by_selection: FilterBySelectionUI,
        batch_edit_captions: BatchEditCaptionsUI,
        update_filter_and_gallery: Callable[[], List],
    ):
        def load_files_from_dir(
            dir: str,
            caption_file_ext: str,
            recursive: bool,
            load_caption_from_filename: bool,
            replace_new_line: bool,
            use_kohya_metadata: bool,
            kohya_json_path: str,
        ):

            dte_instance.load_dataset(
                dir,
                caption_file_ext,
                recursive,
                load_caption_from_filename,
                replace_new_line,
                opts.dataset_editor_use_temp_files,
                kohya_json_path if use_kohya_metadata else None,
                opts.dataset_editor_max_res,
            )
            imgs = dte_instance.get_filtered_imgs(filters=[])
            img_indices = dte_instance.get_filtered_imgindices(filters=[])
            return (
                [imgs, []]
                + [
                    gr.CheckboxGroup.update(
                        value=[str(i) for i in img_indices],
                        choices=[str(i) for i in img_indices],
                    ),
                    1,
                ]
                + filter_by_tags.clear_filters(update_filter_and_gallery)
                + [batch_edit_captions.tag_select_ui_remove.cbg_tags_update()]
            )

        self.btn_load_datasets.click(
            fn=load_files_from_dir,
            inputs=[
                self.tb_img_directory,
                self.tb_caption_file_ext,
                self.cb_load_recursive,
                self.cb_load_caption_from_filename,
                self.cb_replace_new_line_with_comma,
                toprow.cb_save_kohya_metadata,
                toprow.tb_metadata_output,
            ],
            outputs=[
                dataset_gallery.gl_dataset_images,
                filter_by_selection.gl_filter_images,
            ]
            + [
                dataset_gallery.cbg_hidden_dataset_filter,
                dataset_gallery.nb_hidden_dataset_filter_apply,
            ]
            + o_update_filter_and_gallery,
        )

        def unload_files():
            dte_instance.clear()
            return (
                [[], []]
                + [gr.CheckboxGroup.update(value=[], choices=[]), 1]
                + filter_by_tags.clear_filters(update_filter_and_gallery)
                + [batch_edit_captions.tag_select_ui_remove.cbg_tags_update()]
            )

        self.btn_unload_datasets.click(
            fn=unload_files,
            outputs=[
                dataset_gallery.gl_dataset_images,
                filter_by_selection.gl_filter_images,
            ]
            + [
                dataset_gallery.cbg_hidden_dataset_filter,
                dataset_gallery.nb_hidden_dataset_filter_apply,
            ]
            + o_update_filter_and_gallery,
        )
