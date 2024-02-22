import os
import shutil
from urllib.parse import unquote, urlparse

import supervisely as sly
from dataset_tools.convert import unpack_if_archive
from supervisely.io.fs import file_exists, get_file_name
from tqdm import tqdm

import src.settings as s


def download_dataset(teamfiles_dir: str) -> str:
    """Use it for large datasets to convert them on the instance"""
    api = sly.Api.from_env()
    team_id = sly.env.team_id()
    storage_dir = sly.app.get_data_dir()

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, str):
        parsed_url = urlparse(s.DOWNLOAD_ORIGINAL_URL)
        file_name_with_ext = os.path.basename(parsed_url.path)
        file_name_with_ext = unquote(file_name_with_ext)

        sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
        local_path = os.path.join(storage_dir, file_name_with_ext)
        teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

        fsize = api.file.get_directory_size(team_id, teamfiles_dir)
        with tqdm(
            desc=f"Downloading '{file_name_with_ext}' to buffer...",
            total=fsize,
            unit="B",
            unit_scale=True,
        ) as pbar:
            api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)
        dataset_path = unpack_if_archive(local_path)

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, dict):
        for file_name_with_ext, url in s.DOWNLOAD_ORIGINAL_URL.items():
            local_path = os.path.join(storage_dir, file_name_with_ext)
            teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

            if not os.path.exists(get_file_name(local_path)):
                fsize = api.file.get_directory_size(team_id, teamfiles_dir)
                with tqdm(
                    desc=f"Downloading '{file_name_with_ext}' to buffer...",
                    total=fsize,
                    unit="B",
                    unit_scale=True,
                ) as pbar:
                    api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)

                sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
                unpack_if_archive(local_path)
            else:
                sly.logger.info(
                    f"Archive '{file_name_with_ext}' was already unpacked to '{os.path.join(storage_dir, get_file_name(file_name_with_ext))}'. Skipping..."
                )

        dataset_path = storage_dir
    return dataset_path


def count_files(path, extension):
    count = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(extension):
                count += 1
    return count


def convert_and_upload_supervisely_project(
    api: sly.Api, workspace_id: int, project_name: str
) -> sly.ProjectInfo:
    ### Function should read local dataset and upload it to Supervisely project, then return project info.###
    images_path = "/home/alex/DATASETS/TODO/EMDS-6/EMDS5-Original"
    ds_name = "ds"
    batch_size = 30
    masks_path = "/home/alex/DATASETS/TODO/EMDS-6/EMDS5-Ground Truth"

    def create_ann(image_path):
        labels = []
        tags = []

        image_np = sly.imaging.image.read(image_path)[:, :, 0]
        img_height = image_np.shape[0]
        img_wight = image_np.shape[1]

        folder = image_path.split("/")[-2]

        tag = sly.Tag(seq_meta, value=folder)
        tags.append(tag)

        obj_class = folder_to_class[folder]

        mask_path = os.path.join(curr_masks_path, get_file_name(image_path) + "-GTM.png")

        if file_exists(mask_path):
            mask_np = sly.imaging.image.read(mask_path)[:, :, 0]
            mask = mask_np == 255
            curr_bitmap = sly.Bitmap(mask)
            curr_label = sly.Label(curr_bitmap, obj_class)
            labels.append(curr_label)

        return sly.Annotation(img_size=(img_height, img_wight), labels=labels, img_tags=tags)

    project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)

    folder_to_class = {
        "01": sly.ObjClass("actinophrys", sly.Bitmap),
        "02": sly.ObjClass("arcella", sly.Bitmap),
        "03": sly.ObjClass("aspidisca", sly.Bitmap),
        "04": sly.ObjClass("codosiga", sly.Bitmap),
        "05": sly.ObjClass("colpoda", sly.Bitmap),
        "06": sly.ObjClass("epistylis", sly.Bitmap),
        "07": sly.ObjClass("euglypha", sly.Bitmap),
        "08": sly.ObjClass("paramecium", sly.Bitmap),
        "09": sly.ObjClass("rotifera", sly.Bitmap),
        "10": sly.ObjClass("vorticella", sly.Bitmap),
        "11": sly.ObjClass("noctiluca", sly.Bitmap),
        "12": sly.ObjClass("ceratium", sly.Bitmap),
        "13": sly.ObjClass("stentor", sly.Bitmap),
        "14": sly.ObjClass("siprostomum", sly.Bitmap),
        "15": sly.ObjClass("keratella quadrala", sly.Bitmap),
        "16": sly.ObjClass("euglena", sly.Bitmap),
        "17": sly.ObjClass("gymnodinium", sly.Bitmap),
        "18": sly.ObjClass("gonyaulax", sly.Bitmap),
        "19": sly.ObjClass("phacus", sly.Bitmap),
        "20": sly.ObjClass("stylongchia", sly.Bitmap),
        "21": sly.ObjClass("synchaeta", sly.Bitmap),
    }

    seq_meta = sly.TagMeta("sequence", sly.TagValueType.ANY_STRING)

    meta = sly.ProjectMeta(obj_classes=list(folder_to_class.values()), tag_metas=[seq_meta])

    api.project.update_meta(project.id, meta.to_json())

    dataset = api.dataset.create(project.id, ds_name, change_name_if_conflict=True)

    for seq_name in os.listdir(images_path):

        curr_im_path = os.path.join(images_path, seq_name)
        curr_masks_path = os.path.join(masks_path, seq_name)

        images_names = os.listdir(curr_im_path)

        progress = sly.Progress("Create dataset {}".format(ds_name), len(images_names))

        for images_names_batch in sly.batched(images_names, batch_size=batch_size):
            img_pathes_batch = [
                os.path.join(curr_im_path, im_name) for im_name in images_names_batch
            ]

            img_infos = api.image.upload_paths(dataset.id, images_names_batch, img_pathes_batch)
            img_ids = [im_info.id for im_info in img_infos]

            anns = [create_ann(image_path) for image_path in img_pathes_batch]
            api.annotation.upload_anns(img_ids, anns)

            progress.iters_done_report(len(images_names_batch))

    return project
