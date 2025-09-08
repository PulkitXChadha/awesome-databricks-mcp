/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class PromptsService {
    /**
     * List Prompts
     * List all available prompts.
     * @returns string Successful Response
     * @throws ApiError
     */
    public static listPromptsApiPromptsGet(): CancelablePromise<Array<Record<string, string>>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/prompts',
        });
    }
    /**
     * Get Prompt
     * Get the content of a specific prompt.
     * @param promptName
     * @returns string Successful Response
     * @throws ApiError
     */
    public static getPromptApiPromptsPromptNameGet(
        promptName: string,
    ): CancelablePromise<Record<string, string>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/prompts/{prompt_name}',
            path: {
                'prompt_name': promptName,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
