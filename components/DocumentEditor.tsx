
import React, { useState, useRef } from 'react';
import { 
  Upload, 
  Sparkles, 
  Loader2, 
  Download, 
  Trash2, 
  CheckCircle,
  AlertCircle,
  Wand2
} from 'lucide-react';
import { editScholarshipImage } from '../services/geminiService';

interface DocumentEditorProps {
  addPoints: (points: number, action: string) => void;
}

const DocumentEditor: React.FC<DocumentEditorProps> = ({ addPoints }) => {
  const [image, setImage] = useState<string | null>(null);
  const [editedImage, setEditedImage] = useState<string | null>(null);
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImage(reader.result as string);
        setEditedImage(null);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleEdit = async () => {
    if (!image || !prompt.trim()) return;
    setLoading(true);
    try {
      const result = await editScholarshipImage(image, prompt);
      if (result) {
        setEditedImage(result);
        addPoints(15, `Edited document: ${prompt}`);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const downloadImage = () => {
    if (!editedImage) return;
    const link = document.createElement('a');
    link.href = editedImage;
    link.download = 'scholarship_doc_edited.png';
    link.click();
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-slate-900">AI Document Assistant 🪄</h1>
        <p className="text-slate-500">Professionalize your scholarship docs. "Fix lighting", "Remove background", or "Clean artifacts".</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="space-y-4">
          <div 
            className={`aspect-[3/4] rounded-2xl border-2 border-dashed flex flex-col items-center justify-center gap-4 transition-all overflow-hidden bg-white
              ${image ? 'border-green-200' : 'border-slate-300 hover:border-green-400'}`}
          >
            {image ? (
              <div className="relative w-full h-full group">
                <img src={image} alt="Original" className="w-full h-full object-contain" />
                <button 
                  onClick={() => setImage(null)}
                  className="absolute top-4 right-4 p-2 bg-white/90 backdrop-blur rounded-full text-red-500 shadow-sm opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <div className="text-center p-8 space-y-4">
                <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto">
                  <Upload className="w-8 h-8 text-slate-400" />
                </div>
                <div>
                  <p className="font-semibold text-slate-900">Upload your document</p>
                  <p className="text-sm text-slate-400">Passport photo, ID, or certificates</p>
                </div>
                <button 
                  onClick={() => fileInputRef.current?.click()}
                  className="px-6 py-2 bg-green-600 text-white rounded-xl font-semibold shadow-sm hover:bg-green-700 transition-colors"
                >
                  Select File
                </button>
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  onChange={handleFileChange} 
                  className="hidden" 
                  accept="image/*"
                />
              </div>
            )}
          </div>
          
          <div className="bg-amber-50 border border-amber-100 rounded-xl p-4 flex gap-3">
            <AlertCircle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
            <p className="text-xs text-amber-800 leading-relaxed">
              <strong>Tip:</strong> Be specific. Try "Enhance the text clarity" or "Apply a professional bright filter to my passport photo".
            </p>
          </div>
        </div>

        <div className="space-y-6">
          <div className="space-y-4">
            <label className="text-sm font-bold text-slate-700 block">How should I edit this?</label>
            <div className="relative">
              <textarea 
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="e.g. Remove the background and make it plain white for a passport photo"
                className="w-full p-4 bg-white border border-slate-200 rounded-2xl h-32 focus:ring-2 focus:ring-green-500 outline-none resize-none transition-all"
              />
              <div className="absolute bottom-3 right-3 flex gap-2">
                <button 
                  onClick={() => setPrompt("Make it look more professional and sharp")}
                  className="px-3 py-1 bg-slate-100 text-slate-600 text-[10px] font-bold rounded-lg hover:bg-slate-200"
                >
                  Auto-Enhance
                </button>
                <button 
                  onClick={() => setPrompt("Convert to high contrast B&W")}
                  className="px-3 py-1 bg-slate-100 text-slate-600 text-[10px] font-bold rounded-lg hover:bg-slate-200"
                >
                  B&W Mode
                </button>
              </div>
            </div>
            <button 
              onClick={handleEdit}
              disabled={loading || !image || !prompt.trim()}
              className="w-full py-4 bg-green-600 text-white rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-green-700 disabled:bg-slate-300 transition-all shadow-lg shadow-green-100"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Generating Magic...
                </>
              ) : (
                <>
                  <Wand2 className="w-5 h-5" />
                  Process Document
                </>
              )}
            </button>
          </div>

          <div className={`aspect-[3/4] rounded-2xl border-2 border-slate-200 overflow-hidden relative group
            ${editedImage ? 'bg-white' : 'bg-slate-50'}`}>
            {editedImage ? (
              <>
                <img src={editedImage} alt="Edited" className="w-full h-full object-contain" />
                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-3">
                  <div className="bg-green-500 text-white p-2 rounded-full mb-2">
                    <CheckCircle className="w-6 h-6" />
                  </div>
                  <button 
                    onClick={downloadImage}
                    className="flex items-center gap-2 bg-white text-slate-900 px-6 py-2 rounded-xl font-bold hover:bg-slate-100 transition-colors"
                  >
                    <Download className="w-4 h-4" /> Download Result
                  </button>
                </div>
              </>
            ) : (
              <div className="w-full h-full flex flex-col items-center justify-center text-slate-300 space-y-2">
                <Sparkles className="w-12 h-12" />
                <p className="text-sm font-medium">Result will appear here</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentEditor;
