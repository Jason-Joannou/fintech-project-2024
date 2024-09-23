import { getEnviromentVariables } from "../enviroment";
import express, { Response, Request } from "express";
import bodyParser from "body-parser";

// Import routers

// Initialize app
const app = express();

// Middleware
app.use(bodyParser.json());

// Base index route
app.get("/", (req: Request, res: Response) => {
  res.json({
    message: "Welcome to the API! This is the base endpoint.",
  });
});

// Mount routers

const { ilpUrl } = getEnviromentVariables();
const port = 3001;

app.listen(port, () => {
  console.log(`Server running on ${ilpUrl}`);
});
