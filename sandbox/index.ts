import express, {Request, Response} from 'express';

// Create express application
const app = express();
const port = 3000;

// Middleware to parse JSON request bodies
app.use(express.json());

// Routes
app.get('/', (req: Request, res: Response) => {
    res.send('Hello, World!');
});

// URL Parameter
// http://localhost:3000/greet_url/Jason
app.get('/greet_url/:name', (req: Request, res: Response) => {
    const name = req.params.name; // we are accessing the name request from the url
    res.send(`Hello, ${name}!`);
});

//Query Parameter
// http://localhost:3000/greet_query?name=Jason
app.get('/greet_query', (req: Request, res: Response) => {
    const name = req.query.name as string; // we are accessing the name request from the url
    res.send(`Hello, ${name}!`);
});

// Start server
app.listen(port, () => {
    console.log(`Server started on http://localhost:${port}`);
});