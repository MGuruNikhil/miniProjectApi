from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///summary.db'
db = SQLAlchemy(app)

class Summary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Summary('{self.video_id}', '{self.summary}')"

@app.get('/summary')
def summary_api():
    url = request.args.get('url', '')
    video_id = url.split('=')[1]

    summary = Summary.query.filter_by(video_id=video_id).first()
    if summary:
        return jsonify(summary), 200

    summary = get_summary(get_transcript(video_id))
    new_summary = Summary(video_id=video_id, summary=summary)
    db.session.add(new_summary)
    db.session.commit()
    print(summary)
    return jsonify(summary), 200

def get_transcript(video_id):
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    transcript = ' '.join([d['text'] for d in transcript_list])
    print(transcript)
    return transcript

def get_summary(transcript):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    chunk_size = 1000
    chunks = [transcript[i:i+chunk_size] for i in range(0, len(transcript), chunk_size)]
    
    summaries = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=130, min_length=30, do_sample=False)
        summaries.append(summary[0]['summary_text'])
    
    final_summary = ' '.join(summaries)
    return final_summary

if __name__ == '__main__':
    app.run(debug=True)
