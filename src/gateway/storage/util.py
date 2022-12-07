import json

import pika


def upload(f, fs, channel, access):
    # Upload the file to mongodb instance
    try:
        fid = fs.put(f)
    except Exception as err:
        return "internal server error", 500
    # Send message to broker informing service that file is avail
    # to be coverted
    message = { 
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"],
    }

    try:
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE   # messages persisted
            )
        )
    except Exception:
        fs.delete(fid)
        return "internal server error", 500