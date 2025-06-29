from flask import Blueprint, jsonify, request, session
import os
import time
from datetime import datetime
from DB import db
from .models import fileModel
from utility.fileUpload_util import fileUpload
from utility.fileUpload_util import checkFileType
from cloudinary.utils import cloudinary_url
from datetime import timedelta

# Auth middleware
from middlewares.login_middleware import auth, authForAdmin


fileRoutes = Blueprint("files", __name__)
from ..User.models import userModel


@fileRoutes.route("/upload", methods=["POST"])
@auth
@authForAdmin(role="ops")
def uploadFile():
    file = request.files.get("file")
    email = request.form.get("email")

    # user = userModel.getUserInfo(email=email)

    # if user["userType"] != "ops":
    #     return (
    #         jsonify(
    #             {"msg": "client is not allowed to upload the files", "success": False}
    #         ),
    #         400,
    #     )

    if not file or not checkFileType(file.filename):
        return (
            jsonify({"msg": f"File not allowed or invalid file type", "success": False}),
            400,
        )

    url = fileUpload(file, file.filename)

    if not url:
        return jsonify({"msg": "upload failed", "success": False}), 500

    data = fileModel.fileSave(file, email, url)

    return (
        jsonify(
            {
                "msg": "File uploaded",
                "fileTOken": data["downloadFile"],
                "downloadURL": data["url"],
                "success": True,
            }
        ),
        201,
    )


@fileRoutes.route("/uploads", methods=["GET"])
@auth
def getFiles():
    email = request.form.get("email")

    user = userModel.getUserInfo(email=email)

    if not email:
        return jsonify({"msg": "no email provided", "success": False}), 404

    if user is None:
        return (
            jsonify(
                {
                    "msg": "User not found",
                    "success": False,
                }
            ),
            404,
        )

    files = fileModel.getAll()

    dataObject = []
    for each in files:
        dataObject.append(
            {
                "filename": each["filename"],
                "uploadedBy": each["uploadedBy"],
                "url": each["url"],
                "downloadId": each["downloadFile"],
            }
        )

    return (
        jsonify({"msg": "All files are here", "success": True, "files": dataObject}),
        200,
    )


@fileRoutes.route("/download", methods=["GET"])
@auth
def getFile():
    email = request.form.get("email")
    fileId = request.args.get("file")

    user = userModel.getUserInfo(email=email)

    if not email:
        return jsonify({"msg": "no email provided", "success": False}), 404

    if user is None:
        return (
            jsonify(
                {
                    "msg": "User not found",
                    "success": False,
                }
            ),
            404,
        )

    fileFound = fileModel.getFile(fileId)
    expiryTIme = int(time.time() + 30)
    print(f"================================================\n Timestamp: {expiryTIme} \n=============================")
    signedURL, options = cloudinary_url(
        fileFound["publicID"],
        resource_type="raw",
        type="private",
        sign_url=True,
        secure=True,
        timestamp= expiryTIme,
        attachment=fileFound["filename"],
    )
    if fileFound is None:
        return (
            jsonify({"msg": "Invalid file id or file not found", "success": False}),
            404,
        )

    return (
        jsonify(
            {
                "msg": "File found",
                "success": True,
                "data": {
                    "filename": fileFound["filename"],
                    "downloadURL": f"{signedURL}?v={expiryTIme}",
                    "Uploaded By": fileFound["uploadedBy"],
                },
            }
        ),
        200,
    )


@fileRoutes.route("/user-info", methods=["GET"])
def showUserInfo():
    data = request.get_json()
    name = data["username"]

    userExist = userModel.getUserInfo(name)

    if not userExist:
        return jsonify({"msg": "User doesn't exist", "success": False}), 404

    session["username"] = name

    return jsonify({"msg": "Session Data stored", "success": True}), 200
