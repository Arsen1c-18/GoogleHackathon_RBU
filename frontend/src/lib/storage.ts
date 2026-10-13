import { ref, uploadBytes, getDownloadURL } from "firebase/storage";
import { storage } from "./firebase-client";

export async function uploadUserFile(uid: string, file: File): Promise<string> {
  const path = `uploads/${uid}/${Date.now()}-${file.name}`;
  const fileRef = ref(storage, path);
  await uploadBytes(fileRef, file);
  return getDownloadURL(fileRef);
}

/** Persist a voice-complaint recording under the owner's path.
 *  Matches storage.rules complaints/{uid}/** (owner-only, <10 MB). */
export async function uploadComplaintAudio(
  uid: string,
  audio: Blob
): Promise<string> {
  const stamp = Date.now();
  const rand = Math.random().toString(36).slice(2, 10);
  const path = `complaints/${uid}/${stamp}-${rand}.webm`;
  const fileRef = ref(storage, path);
  await uploadBytes(fileRef, audio, { contentType: "audio/webm" });
  return getDownloadURL(fileRef);
}
