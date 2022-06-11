import firebase_admin
from firebase_admin import credentials,firestore
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
from sklearn import svm
from sklearn.model_selection import train_test_split
import re
from flask import Flask, render_template, request
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn import svm
import string
from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Mail, Message
ques=[]


ans=[]
cred = credentials.Certificate("G:/7 sem/curiosity/src/flaskserver/serviceAccount.json")
firebase_admin.initialize_app(cred)
db=firestore.client()
def contact():
    with app.app_context():
         contact=db.collection('contacts').get()
         for c in contact:
            res=c.to_dict()
            name=res["name"]
            message=res["message"]
            cmail=res["mail"]
            if cmail == False:
                msg = Message('Feedback from Curiosity', sender = 'aditiagrawal1023@gmail.com', recipients =['aditiagrawal1023@gmail.com'])
                msg.body = "From " +name+" Feedback:"+message; 
                mail.send(msg)
                print("sent mail")
                up = db.collection(u'contacts').document(c.id)
                up.update({u'mail': True})

def dupplicate():
    with app.app_context():
        questions=db.collection('questions').get()
        for q in questions:
            res=q.to_dict()
            dupcheckq=res["question"]
            dupcheckt=res["timestamp"]
            for d in questions:
                dup=d.to_dict()

                if dupcheckt!=dup["timestamp"]:
                    if dupcheckq==dup["question"]:
                        if dupcheckt<dup["timestamp"]:
                            print("Dupplicate Deleted")
                            print(dup["question"])
                            docs=db.collection('questions').document(d.id).collection('answer').get()
                            for doc in docs:
                                db.collection('questions').document(d.id).collection('answer').document(doc.id).delete()
                            db.collection('questions').document(d.id).delete() 
                        else:
                            print("Dupplicate Deleted")
                            print(res["question"])
                            docs=db.collection('questions').document(q.id).collection('answer').get()
                            for doc in docs:
                                db.collection('questions').document(q.id).collection('answer').document(doc.id).delete()
                            db.collection('questions').document(q.id).delete()


df = pd.read_csv("G:/7 sem/curiosity/train_E6oV3lV.csv.zip")
hate_sp = df[df.label == 1]
normal_sp = df[df.label == 0]

def process_tweet(tweet):
    return " ".join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])", " ",tweet.lower()).split())    
df['processed_tweets'] = df['tweet'].apply(process_tweet)
cnt_non_fraud = df[df['label'] == 0]['processed_tweets'].count()
df_class_fraud = df[df['label'] == 1]
df_class_nonfraud = df[df['label'] == 0]
df_class_fraud_oversample = df_class_fraud.sample(cnt_non_fraud, replace=True)
df_oversampled = pd.concat([df_class_nonfraud, df_class_fraud_oversample], axis=0)
from sklearn.model_selection import train_test_split
X = df_oversampled['processed_tweets']
y = df_oversampled['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify = None)


count_vect = CountVectorizer(stop_words='english')
transformer = TfidfTransformer(norm='l2',sublinear_tf=True)
x_train_counts = count_vect.fit_transform(X_train)
x_train_tfidf = transformer.fit_transform(x_train_counts)

#SVM Model
model = svm.LinearSVC()
model.fit(x_train_tfidf,y_train)

def schedule():
    with app.app_context():
        questions=db.collection('questions').get()
        User=db.collection('User').get()
        for q in questions:
            res=q.to_dict()
            X_new = []
            question=res["question"]
            user_review = [ question]
            for review in user_review:
                X_new.append(process_tweet(review))
            X_new = count_vect.transform(X_new)
            X_new = transformer.transform(X_new)
            X_new = X_new.toarray()
            predict_svm = model.predict(X_new)
            for analysis in predict_svm:
                speech = analysis
            speech = np.where(speech, 'Hate', 'Normal')
            if speech == 'Hate':
                ques.append(res["question"])
                
                HEmail=res['user']['email']
                msg = Message('Curiosity', sender = 'radhikaagrawal@gmail.com', recipients = [HEmail])
                msg.body = "Your Question post contain Hate speech. The question is "+question+" Hence, Deleted."
                mail.send(msg)
                for i in User:
                    ituser=i.to_dict()
                    if HEmail==ituser['email']: 
                        db.collection('User').document(i.id).update({
                            'notification' : "HateSpeech Found in your post, Thats why removed",
                        })
                        
            
                x=0
                if x==0:
                    docs=db.collection('questions').document(q.id).collection('answer').get()
                    for doc in docs:              
                        db.collection('questions').document(q.id).collection('answer').document(doc.id).delete()
                db.collection('questions').document(q.id).delete()      
                print("Deleted")
            docs=db.collection('questions').document(q.id).collection('answer').get()
            
            for doc in docs:
                res=doc.to_dict()
                X_new = []
                answer=res["answer"]
                user_review = [ answer]
                for review in user_review:
                    X_new.append(process_tweet(review))
                    X_new = count_vect.transform(X_new)
                    X_new = transformer.transform(X_new)
                    X_new = X_new.toarray()
                predict_svm = model.predict(X_new)
                for analysis in predict_svm:
                    speech = analysis
                speech = np.where(speech, 'Hate', 'Normal')
                if speech == 'Hate':
                    AEmail=res['user']['email']
                    msg = Message('Curiosity', sender = 'radhikaagrawal@gmail.com', recipients = [AEmail])
                    msg.body = "Your Answer post contain Hate speech. The answer is "+answer+" Hence, Deleted."
                    mail.send(msg)
                    ans.append(res["answer"])
                    db.collection('questions').document(q.id).collection('answer').document(doc.id).delete()
                    print("Deleted")
            

app=Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.add_job(func=schedule, trigger="interval", seconds=30)
scheduler.add_job(func=dupplicate, trigger="interval", seconds=30)
scheduler.add_job(func=contact, trigger="interval", seconds=20)
scheduler.start()
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'radhikaagrawal@gmail.com'
app.config['MAIL_PASSWORD'] ='password'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail= Mail(app)
@app.route('/')
def index():
     return render_template('Hatespeech.html', question=ques, answer=ans)

if __name__=='__main__': 
    app.run(debug=True)