import { getEnviromentVariables } from "../enviroment/index";
import express, { Response, Request } from "express";
import bodyParser from "body-parser";
import payments from "./routes/payments";
import swaggerJsDoc from "swagger-jsdoc";
import swaggerUi from "swagger-ui-express";

// Import routers

// Initialize app
const app = express();

// Middleware
app.use(bodyParser.json());

// Swagger definition
const swaggerOptions = {
  swaggerDefinition: {
    openapi: "3.0.0",
    info: {
      title: "DigiStokvel Express API",
      version: "1.0.0",
      description: "API Documentation for DigiStokvel's Express App",
      contact: {
        name: "Support",
        email: "support@example.com",
      },
    },
    servers: [
      {
        url: "http://localhost:3001",
        description: "Local Development Server",
      },
    ],
  },
  apis: ["./api/routes/*.ts", "./api/*.ts"], // Path to the API docs
};

// Initialize Swagger
const swaggerDocs = swaggerJsDoc(swaggerOptions);
app.use("/docs", swaggerUi.serve, swaggerUi.setup(swaggerDocs));

// Base index route
/**
 * @swagger
 * /:
 *   get:
 *     summary: Base Index Endpoint
 *     description: Returns a welcome message for the DigiStokvel API.
 *     responses:
 *       200:
 *         description: A JSON object containing a welcome message.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                   example: "Welcome to the API! This is the base endpoint."
 */
app.get("/", (req: Request, res: Response) => {
  res.json({
    message: "Welcome to the API! This is the base endpoint.",
  });
});

app.get("/", (req: Request, res: Response) => {
  res.json({
    message: "Welcome to the API! This is the base endpoint.",
  });
});

// Mount routers to base paths
app.use("/payments", payments);

const { ilpUrl } = getEnviromentVariables();
const port = 3001;

app.listen(port, () => {
  console.log(`Server running on ${ilpUrl}`);
});
