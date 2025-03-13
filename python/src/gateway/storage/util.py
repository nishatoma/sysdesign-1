import pika, json

def upload(f, fs, channel, access):
    #First upload the file to MDB.
    try:
        fid = fs.put(f)
    except Exception as err:
        return "internal server error", 500
    
    # 2) Put a message in Rabbit MQ.
    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"]
    }

    try:
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except:
        # Delete stale files if the message cant be put in Q
        fs.delete(fid)
        return "internal server error", 500