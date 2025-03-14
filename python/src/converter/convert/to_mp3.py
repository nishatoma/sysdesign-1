import pika, json, tempfile, os
from bson.objectid import ObjectId
from moviepy import VideoFileClip

def start(message, fs_videos, fs_mp3, channel):
    message = json.loads(message)

    # Empty temp file
    tf = tempfile.NamedTemporaryFile()
    # video contents
    out = fs_videos.get(ObjectId(message["video_fid"]))
    # add video contents to emptt file
    tf.write(out.read())
    # create audio from temp video file
    audio = VideoFileClip(tf.name).audio
    tf.close()

    # Write hte audio to its file
    tf_path = tempfile.gettempdir() + f"/{message['video_fid']}.mp3"
    audio.write_audiofile(tf_path)

    # save file to mongo
    f = open(tf_path, "rb")
    data = f.read()
    fid = fs_mp3s.put(data)
    f.close()
    os.remove(tf_path)

    message["mp3_fid"] = str(fid)

    # put message to new quque
    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("MP3_QUEUE"),
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
    except Exception as err:
        fs_mp3s.delete(fid)
        return "Failed to publish message"
