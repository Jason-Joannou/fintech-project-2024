import amqp, { Connection, Channel } from 'amqplib';

let connection: Connection;
let channel: Channel;

const queue = 'default_queue';

const connect = async () => {
  if (!connection) {
    connection = await amqp.connect('amqp://localhost');
  }
  if (!channel) {
    channel = await connection.createChannel();
  }
};

export const sendMessageToQueue = async (message: string, queueName: string = queue): Promise<void> => {
  try {
    await connect();
    await channel.assertQueue(queueName, { durable: false });
    channel.sendToQueue(queueName, Buffer.from(message));
    console.log(`Sent: ${message}`);
  } catch (error) {
    console.error('Error sending message to queue:', error);
  }
};

export const receiveMessageFromQueue = async (queueName: string = queue, callback: (msg: string) => void): Promise<void> => {
  try {
    await connect();
    await channel.assertQueue(queueName, { durable: false });
    console.log('Waiting for messages in %s. To exit press CTRL+C', queueName);

    channel.consume(queueName, (msg) => {
      if (msg !== null) {
        const message = msg.content.toString();
        console.log(`Received: ${message}`);
        callback(message);
        channel.ack(msg);
      }
    });
  } catch (error) {
    console.error('Error receiving message from queue:', error);
  }
};

export const closeConnection = async () => {
  try {
    if (channel) {
      await channel.close();
    }
    if (connection) {
      await connection.close();
    }
  } catch (error) {
    console.error('Error closing connection:', error);
  }
};