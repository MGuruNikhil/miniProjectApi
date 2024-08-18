from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///summary.db'
db = SQLAlchemy(app)

class Summary(db.Model):
    video_id = db.Column(db.String, primary_key=True)
    summary = db.Column(db.String)

    def to_dict(self):
        return {
            'video_id': self.video_id,
            'summary': self.summary
        }

@app.get('/summary')
def summary_api():
    url = request.args.get('url', '')
    if not url:
        return jsonify({"error": "URL parameter is missing"}), 400

    video_id = url.split('=')[1] if '=' in url else None
    if not video_id:
        return jsonify({"error": "Invalid URL format"}), 400

    summary = Summary.query.filter_by(video_id=video_id).first()
    if summary:
        print(f"Summary found in DB: {summary.to_dict()}")
        return jsonify(summary.to_dict()), 200

    summary_text = get_summary(get_transcript(video_id))
    print(f"Generated summary: {summary_text}")

    new_summary = Summary(video_id=video_id, summary=summary_text)
    db.session.add(new_summary)
    db.session.commit()

    # Fetch the newly added summary to ensure it's committed
    summary = Summary.query.filter_by(video_id=video_id).first()
    if summary:
        print(f"New summary saved to DB: {summary.to_dict()}")
        return jsonify(summary.to_dict()), 200
    else:
        return jsonify({"error": "Failed to save summary"}), 500

def get_transcript(video_id):
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    transcript = ' '.join([d['text'] for d in transcript_list])
    print(transcript)
    return transcript

def get_summary(transcript):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    chunk_size = 1000
    chunks = [transcript[i:i+chunk_size] for i in range(0, len(transcript), chunk_size)]
    
    summary = ' '.join([summarizer(chunk)[0]['summary_text'] for chunk in chunks])
    return summary

if __name__ == '__main__':
    app.run(debug=True)
