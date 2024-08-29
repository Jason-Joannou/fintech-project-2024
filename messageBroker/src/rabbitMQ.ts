import amqp, { Connection, Channel } from 'amqplib';

let connection: Connection;
const channels: { [key: string]: Channel } = {};

const connect = async () => {
  if (!connection) {
    connection = await amqp.connect('amqp://localhost');
  }
};

const getChannel = async (channelName: string): Promise<Channel> => {
  if (!channels[channelName]) {
    await connect();
    const channel = await connection.createChannel();
    channels[channelName] = channel;
  }
  return channels[channelName];
};

export const sendMessageToQueue = async (message: string, queueName: string = 'default_queue', channelName: string = 'default'): Promise<void> => {
  try {
    const channel = await getChannel(channelName);
    await channel.assertQueue(queueName, { durable: false });
    channel.sendToQueue(queueName, Buffer.from(message));
    console.log(`Sent: ${message}`);
  } catch (error) {
    console.error('Error sending message to queue:', error);
  }
};

export const receiveMessageFromQueue = async (queueName: string = 'default_queue', callback: (msg: string) => void, channelName: string = 'default'): Promise<void> => {
  try {
    const channel = await getChannel(channelName);
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
    for (const channelName in channels) {
      await channels[channelName].close();
    }
    if (connection) {
      await connection.close();
    }
  } catch (error) {
    console.error('Error closing connection:', error);
  }
};