import { writable } from "svelte/store";

export const alerts = writable<{ id: string; status: string }[]>([]);

// You could update this store via a WebSocket connection
