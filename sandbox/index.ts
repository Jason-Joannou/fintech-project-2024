import express, {Request, Response} from 'express';

// Interfaces
interface GreetQuery {
    name: string;
}

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
app.get('/greet_query', (req: Request<{}, {}, {}, GreetQuery>, res: Response) => {
    const name = req.query.name as string; // we are accessing the name request from the url
    res.send(`Hello, ${name}!`);
});

// POST Request
// simple pay
app.post('/pay', (req: Request, res: Response) => {
    const amount = req.body.amount; // we are accessing the amount request from the body
    res.send(`Pay ${amount}!`);
});

// Start server
app.listen(port, () => {
    console.log(`Server started on http://localhost:${port}`);
});