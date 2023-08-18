import omero
import omero.cli
from omero.rtypes import  rstring
import csv
import os

base_dir = "/uod/idr/metadata/idr0150-friedman-cafs/ROIs"

def get_images(conn):
    project = conn.getObject("Project", attributes={"name": "idr0150-friedman-cafs/experimentA"})
    for dataset in project.listChildren():
        for image in dataset.listChildren():
            yield dataset, image


def get_points(path):
    point_str = ""
    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            point_str += f"{row['x']},{row['y']}, "
        point_str = point_str[0:len(point_str)-2]
    return point_str


def create_roi(image, point_str):
    """
    Creates a polygon ROI
    :param image: The image
    :param point_str: The points as string (x1,y1, x2,y2, ...)
    :return: The ROI
    """
    roi = omero.model.RoiI()
    roi.setImage(image._obj)
    pg = omero.model.PolygonI()
    pg.points = rstring(point_str)
    roi.addShape(pg)
    return roi


def delete_rois(conn, im):
    result = conn.getRoiService().findByImage(im.id, None)
    to_delete = []
    for roi in result.rois:
        to_delete.append(roi.getId().getValue())
    if to_delete:
        print(f"Deleting existing {len(to_delete)} rois on image {im.name}.")
        conn.deleteObjects("Roi", to_delete, deleteChildren=True, wait=True)


with omero.cli.cli_login() as c:
    conn = omero.gateway.BlitzGateway(client_obj=c.get_client())
    update_service = conn.getUpdateService()
    for ds, img in get_images(conn):
        delete_rois(conn, img)
        img_basename = img.getName().replace(".tiff", "")
        roi_file = f"{base_dir}/{ds.getName()}/{img_basename}.roi.csv"
        if not os.path.isfile(roi_file):
            print(f"{roi_file} not found!")
            continue
        point_str = get_points(roi_file)
        roi = create_roi(img, point_str)
        update_service.saveObject(roi)
        print(f"Added ROI for {img.getName()}")
