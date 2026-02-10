
import { GoogleGenAI, Type, GenerateContentResponse } from "@google/genai";
import { Scholarship } from "../types";

const API_KEY = process.env.API_KEY || "";

export const searchScholarships = async (query: string): Promise<{ scholarships: Scholarship[]; sources: any[] }> => {
  const ai = new GoogleGenAI({ apiKey: API_KEY });
  const prompt = `Search for the latest graduate scholarships for Nigerian students related to: ${query}. 
  Return the results as a JSON array of scholarship objects with fields: 
  id, title, country, deadline, funding (Full, Partial, or Tuition Only), degree (Masters, PhD, or PostDoc), description, and link.
  
  Make sure the results are current for the 2024/2025 or 2025/2026 academic year.`;

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
            deadline: { type: Type.STRING },
            funding: { type: Type.STRING },
            degree: { type: Type.STRING },
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

export const editScholarshipImage = async (base64Image: string, prompt: string): Promise<string | null> => {
  const ai = new GoogleGenAI({ apiKey: API_KEY });
  
  const response = await ai.models.generateContent({
    model: 'gemini-2.5-flash-image',
    contents: {
      parts: [
        {
          inlineData: {
            data: base64Image.split(',')[1],
            mimeType: 'image/png',
          },
        },
        {
          text: `Edit this scholarship document image as follows: ${prompt}. Return the edited image.`,
        },
      ],
    },
  });

  for (const part of response.candidates?.[0]?.content?.parts || []) {
    if (part.inlineData) {
      return `data:image/png;base64,${part.inlineData.data}`;
    }
  }

  return null;
};
