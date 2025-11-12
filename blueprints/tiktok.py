# pylint: skip-file
from flask import Blueprint, request, jsonify
from helpers.download import videoDL,videoDL_for_insta
from utils.valid import check_platform

dl_bp = Blueprint("tiktok", __name__, url_prefix='/dl')


@dl_bp.route('/tiktok')
def tiktok():
    data = request.args
    url = data.get("url")
    if (not url):
        return jsonify({'message': 'No url found in the query'}), 400
    platform = check_platform(url)
    if platform != "tiktok":
        return jsonify({
            'message': 'Not a valid tiktok url'
        }), 400
    info = videoDL(url)

    return jsonify(info)


@dl_bp.route('/insta')
def instagram():
    data = request.args
    url = data.get("url")
    if (not url):
        return jsonify({'message': 'No url found in the query'}), 400
    platform = check_platform(url)
    if platform != "instagram":
        return jsonify({
            'message': 'Not a valid Instagram url'
        }), 400
    info = videoDL_for_insta(url)
    return jsonify(info)


@dl_bp.route('/yt')
def youtube():
    """Downloads a YouTube video using yt_dlp."""
    data = request.args
    if not (data.get("url")):
        return jsonify({'message': 'No url found in the query'}), 400
    platform = check_platform(data.get("url"))
    if platform != "youtube":
        return jsonify({
            'message': 'Not a valid Youtube url'
        }), 400
    info = videoDL(data.get("url"))
    return jsonify(info)

@dl_bp.route('/fb')
def facebook():
    """Downloads a Facebook video using yt_dlp."""
    data = request.args
    if not (data.get("url")):
        return jsonify({'message': 'No url found in the query'}), 400
    platform = check_platform(data.get("url"))
    if platform != "facebook":
        return jsonify({
            'message': 'Not a valid Youtube url'
        }), 400
    info = videoDL(data.get("url"))
    return jsonify(info)


