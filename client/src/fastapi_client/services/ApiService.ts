/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserInfo } from '../models/UserInfo';
import type { UserWorkspaceInfo } from '../models/UserWorkspaceInfo';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ApiService {
    /**
     * Get Current User
     * Get current user information from Databricks.
     * @returns UserInfo Successful Response
     * @throws ApiError
     */
    public static getCurrentUserApiUserMeGet(): CancelablePromise<UserInfo> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/user/me',
        });
    }
    /**
     * Get User Workspace Info
     * Get user information along with workspace details.
     * @returns UserWorkspaceInfo Successful Response
     * @throws ApiError
     */
    public static getUserWorkspaceInfoApiUserMeWorkspaceGet(): CancelablePromise<UserWorkspaceInfo> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/user/me/workspace',
        });
    }
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
    /**
     * Get Mcp Info
     * Get MCP server information including URL and capabilities.
     *
     * Returns:
     * Dictionary with MCP server details
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getMcpInfoApiMcpInfoInfoGet(): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/mcp_info/info',
        });
    }
    /**
     * Get Mcp Discovery
     * Get MCP discovery information including prompts and tools.
     *
     * This endpoint dynamically discovers available prompts and tools
     * from the FastMCP server instance.
     *
     * Returns:
     * Dictionary with prompts and tools lists and servername
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getMcpDiscoveryApiMcpInfoDiscoveryGet(): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/mcp_info/discovery',
        });
    }
    /**
     * Get Mcp Config
     * Get MCP configuration for Claude Code setup.
     *
     * Returns:
     * Dictionary with configuration needed for Claude MCP setup
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getMcpConfigApiMcpInfoConfigGet(): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/mcp_info/config',
        });
    }
    /**
     * Get Mcp Prompt Content
     * Get the content of a specific MCP prompt.
     *
     * Args:
     * prompt_name: The name of the prompt
     *
     * Returns:
     * Dictionary with prompt name and content
     * @param promptName
     * @returns string Successful Response
     * @throws ApiError
     */
    public static getMcpPromptContentApiMcpInfoPromptPromptNameGet(
        promptName: string,
    ): CancelablePromise<Record<string, string>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/mcp_info/prompt/{prompt_name}',
            path: {
                'prompt_name': promptName,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
