import { ref, uploadBytes, getDownloadURL } from "firebase/storage";
import { storage } from "./firebase-client";

export async function uploadUserFile(uid: string, file: File): Promise<string> {
  const path = `uploads/${uid}/${Date.now()}-${file.name}`;
  const fileRef = ref(storage, path);
  await uploadBytes(fileRef, file);
  return getDownloadURL(fileRef);
}
