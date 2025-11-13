import asyncio
import json
import requests
from flask import jsonify, Blueprint, request, Response
from helpers.anime_helper import get_kiwi_url, get_redirect_link
from helpers.anime_helper import get_animepahe_cookies, get_pahewin_link
from helpers.anime_helper import get_actual_episode, get_cached_anime_info, get_episode_session
from utils.helper import encodeURIComponent
from utils.generate import generate_internal_id
from db import get_db

anime_bp = Blueprint("anime", __name__, url_prefix="/anime")


@anime_bp.route("/search", methods=["GET"])
def anime_search():
    query = request.args.get("query")
    if query is None:
        return jsonify({
            'status': 400,
            'message': "Query is Required"
        }), 400
    if not query:
        return jsonify({
            'status': 400,
            'message': "No query found"
        }), 400

    search_result = []
    cookies = asyncio.run(get_animepahe_cookies())
    res = requests.get(
        f"https://animepahe.si/api?m=search&q={encodeURIComponent(query)}", cookies=cookies,
        timeout=10)
    results = res.json()
    info = results.get('data')
    # return "hello"
    db = get_db()
    for i in info:
        cursor = db.execute(
            "SELECT internal_id FROM anime_info WHERE external_id = ?", (i.get("session"),))
        row = cursor.fetchone()
        episodes = get_actual_episode(i.get("session")) if i.get(
            "episodes") == 0 or i.get("status") == "Currently Airing" else i.get("episodes")
        if not row or not row["internal_id"]:
            internal_id = generate_internal_id(i.get("title"))
            db.execute("INSERT INTO anime_info(internal_id,external_id,title,episodes) VALUES(?,?,?,?)",
                       (internal_id, i.get("session"), i.get("title"), episodes))
            db.commit()
        else:
            internal_id = row["internal_id"]
        filtered_search_result = {
            "id": internal_id,
            "title": i.get("title"),
            "episodes": episodes,
            "status": i.get("status"),
            "year": i.get("year"),
            "rating": i.get("score")
        }
        search_result.append(filtered_search_result)
    return Response(json.dumps({
        'status': 200,
        'result': search_result
    }, sort_keys=False), mimetype='application/json')


@anime_bp.route("/download", methods=["GET"])
def anime_download():
    id = request.args.get("id")
    episode = request.args.get("episode")
    if not id:
        return jsonify({
            "status": 400,
            "message": "Id of anime is required"
        }), 400
    if not episode:
        return jsonify({
            "status": 400,
            "message": "episode number of anime is required"
        }), 400
    if not str.isdigit(episode):
        return jsonify({
            "status": 400,
            "message": "Episode query is Not a Number"
        }), 400

    info = get_cached_anime_info(id)
    if not info:
        return jsonify({
            "status": 404,
            "message": "No results found"
        }), 404
    ep_count = info["episodes"]
    if int(episode) > int(ep_count):
        return jsonify({
            "status": 422,
            "message": "Episode number exceed available count"
        }), 422
    if not info["external_id"]:
        return jsonify({
            "status": 404,
            "message": "No external id found"
        }), 404
    if int(episode)<= 0:
        return jsonify({
            "status":400,
            "message": "Episode count cannot be zero or below"
        }),400
    db = get_db()
    cursor = db.execute(
        "SELECT * FROM cached_video_url WHERE internal_id = ? and episode = ?", (id, episode))
    row = cursor.fetchone()
    if row and row["video_url"]:
        link = row["video_url"]
        res = requests.head(link, timeout=10)
        if res.status_code == 200:
            return jsonify({
                "status": 200,
                "direct_link": row["video_url"],
                "size": row["size"],
                "episode": row["episode"]
            })
    search_result = get_episode_session(info["external_id"])
    episode_info = search_result[int(episode)-1]
    episode_session = episode_info.get("session")
    pahe_link = get_pahewin_link(info["external_id"], episode_session)
    if pahe_link is None:
        return jsonify({
            "status": 404,
            "message": "Internal Link not found"
        }), 404
    kiwi_url = asyncio.run(get_kiwi_url(pahe_link))
    results = get_redirect_link(kiwi_url, id, episode)
    return jsonify(results),500 if results.get("status") == 500 else 200
@anime_bp.route("/bulk-download")
def anime_bulk_downloading():
    id = request.args.get("id")
    ep_from = request.args.get("from")
    ep_to = request.args.get("to")
    if not ep_from or not ep_to or not id:
        return jsonify({
            'status': 400,
            'message': "Fields Are required (from,to,id)"
        }),400
    if int(ep_from) > int(ep_to):
        return jsonify({
            "status":400,
            "message":"From cannot be greater than to"
        }),400
    if int(ep_from) <= 0 or int(ep_to) <= 0:
        return jsonify({
            "status":400,
            "message": "Episode count cannot be zero or below"
        }),400
    info = get_cached_anime_info(id)
    if not info:
        return jsonify({
            "status": 404,
            "message": "No results found"
        }), 404
    ep_count = info["episodes"]
    if int(ep_to) > int(ep_count) or int(ep_from) > int(ep_count):
        return jsonify({
            "status": 422,
            "episodes":ep_count,
            "message": "Episode number exceed available count"
        }),422
    if not info["external_id"]:
        return jsonify({
            "status": 404,
            "message": "No external id found"
        }), 404
    download_link = []
    for episode in range(int(ep_from),int(ep_to)+1):
        db = get_db()
        cursor = db.execute(
            "SELECT * FROM cached_video_url WHERE internal_id = ? and episode = ?", (id, episode))
        row = cursor.fetchone()
        if row and row["video_url"]:
            link = row["video_url"]
            res = requests.head(link, timeout=10)
            if res.status_code == 200:
                download_link.append({
                    "status": 200,
                    "direct_link": row["video_url"],
                    "size": row["size"],
                    "episode": row["episode"]
                })
                continue
        search_result = get_episode_session(info["external_id"])
        episode_info = search_result[int(episode)-1]
        episode_session = episode_info.get("session")
        pahe_link = get_pahewin_link(info["external_id"], episode_session)
        if pahe_link is None:
            return jsonify({
                "status": 404,
                "message": "Internal Link not found"
            }), 404
        kiwi_url = asyncio.run(get_kiwi_url(pahe_link))
        results = get_redirect_link(kiwi_url, id, episode)
        download_link.append(results)
    return download_link
    
