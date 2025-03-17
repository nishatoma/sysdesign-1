import pika, sys, os, time
from pymongo import MongoClient
import gridfs
from convert import to_mp3
import config

def main():
    print("Starting Consumer...")  # Debugging
    print(f"Connecting to MongoDB at {config.MONGO_URI}")

    # MongoDB connection
    client = MongoClient(config.MONGO_URI)
    db_videos = client["videos"]
    db_mp3s = client["mp3s"]

    print("Connected to MongoDB!")

    # GridFS
    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s = gridfs.GridFS(db_mp3s)

    # RabbitMQ connection
    print("Connecting to RabbitMQ...")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()
    print("Connected to RabbitMQ!")

    def callback(ch, method, properties, body):
        print(f"Received message: {body}")  # Debugging
        err = to_mp3.start(body, fs_videos, fs_mp3s, ch)
        if err:
            print(f"Error processing file: {err}")
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=os.environ.get("VIDEO_QUEUE"), on_message_callback=callback
    )

    print("Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        sys.exit(0)