import firebase from "firebase";

const firebaseConfig = {
//You have to copy Api Key of your project from firebase and paste here
};
//const firebaseApp;
//export default !firebase.apps.length ? firebase.initializeApp(firebaseconfig) : firebase.app();
const firebaseApp = firebase.initializeApp(firebaseConfig);


const auth = firebase.auth();
const provider = new firebase.auth.GoogleAuthProvider();
const db = firebaseApp.firestore();

export { auth, provider };
export default db;
