
import { GoogleGenAI, Type } from "@google/genai";
import { Scholarship } from "../types";

const API_KEY = process.env.API_KEY || "";

export const searchScholarships = async (query: string): Promise<{ scholarships: Scholarship[]; sources: any[] }> => {
  const ai = new GoogleGenAI({ apiKey: API_KEY });
  const prompt = `Search for the latest graduate scholarships from anywhere in the world related to: ${query}.
  Return the results as a JSON array of scholarship objects with fields:
  id, title, country, region, university, deadline, funding (Full, Partial, or Tuition Only), degree (Masters, PhD, or PostDoc), field, description, and link.

  Only include scholarships open for the 2026/2027 academic year or later.`;

  const response = await ai.models.generateContent({
    model: 'gemini-3-flash-preview',
    contents: prompt,
    config: {
      tools: [{ googleSearch: {} }],
      responseMimeType: "application/json",
      responseSchema: {
        type: Type.ARRAY,
        items: {
          type: Type.OBJECT,
          properties: {
            id: { type: Type.STRING },
            title: { type: Type.STRING },
            country: { type: Type.STRING },
            region: { type: Type.STRING },
            university: { type: Type.STRING },
            deadline: { type: Type.STRING },
            funding: { type: Type.STRING },
            degree: { type: Type.STRING },
            field: { type: Type.STRING },
            description: { type: Type.STRING },
            link: { type: Type.STRING },
          },
          required: ["id", "title", "country", "deadline", "funding", "degree", "description", "link"]
        }
      }
    },
  });

  let scholarships: Scholarship[] = [];
  try {
    scholarships = JSON.parse(response.text || "[]");
  } catch (e) {
    console.error("Failed to parse scholarship JSON", e);
  }

  const sources = response.candidates?.[0]?.groundingMetadata?.groundingChunks || [];

  return { scholarships, sources };
};
