import { sendMessageToQueue, receiveMessageFromQueue, closeConnection } from '../src/rabbitMQ';

describe('RabbitMQ Message Broker', () => {
  afterAll(async () => {
    await closeConnection();
  });

  it('should send and receive messages', (done) => {
    const testQueue = 'test_queue';
    const testMessage = 'Hello, RabbitMQ!';

    // Increase the timeout for this test
    jest.setTimeout(10000);

    // Start the consumer first
    receiveMessageFromQueue(testQueue, (msg) => {
      try {
        expect(msg).toBe(testMessage);
        done();
      } catch (error) {
        done(error);
      }
    });

    // Send the message
    sendMessageToQueue(testMessage, testQueue);
  });
});