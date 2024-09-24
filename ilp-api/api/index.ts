import { getEnviromentVariables } from "../enviroment/index";
import express, { Response, Request } from "express";
import bodyParser from "body-parser";
import payments from "./routes/payments";

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

// Mount routers to base paths
app.use("/payments", payments);

const { ilpUrl } = getEnviromentVariables();
const port = 3001;

app.listen(port, () => {
  console.log(`Server running on ${ilpUrl}`);
});
