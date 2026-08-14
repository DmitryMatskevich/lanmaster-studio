import { StudioApiClient } from "../../clients/typescript/src";

export type StudioRole = "viewer" | "engineer" | "admin";

export interface SessionState {
  subject: string;
  role: StudioRole;
}

export function createStudioClient(session: SessionState): StudioApiClient {
  return new StudioApiClient("", {
    "X-Dev-User": session.subject,
    "X-Dev-Roles": session.role
  });
}
