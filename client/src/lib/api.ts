import { OpenAPI, PromptsService } from "@/fastapi_client";

// Configure the API client
OpenAPI.BASE = "/api";

// Export the services as apiClient
export const apiClient = {
  prompts: PromptsService,
};
