import { GoogleGenerativeAI } from "@google/generative-ai";

export default async function handler(req, res) {
    // Configuração de Headers para evitar problemas de CORS no deploy
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Apenas POST é permitido' });
    }

    const { theme } = req.body;
    const API_KEY = process.env.GEMINI_API_KEY;

    if (!API_KEY) {
        return res.status(500).json({ error: 'Variável GEMINI_API_KEY não encontrada no ambiente Vercel.' });
    }

    try {
        const genAI = new GoogleGenerativeAI(API_KEY);
        const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

        const prompt = `Atue como especialista em LinkedIn. Tema: ${theme}. 
        Gere um post com: 1. Gancho forte. 2. Parágrafos curtos. 3. Call to Action. 
        Mantenha o foco em UX Writing.`;

        const result = await model.generateContent(prompt);
        const response = await result.response;
        
        return res.status(200).json({ text: response.text() });
    } catch (error) {
        console.error("Erro na API:", error);
        return res.status(500).json({ error: 'Erro interno ao processar IA.' });
    }
}
