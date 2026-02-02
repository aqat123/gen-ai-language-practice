package com.fluencia.app.data.api

import com.fluencia.app.data.local.TokenManager
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import okhttp3.Interceptor
import okhttp3.Response
import javax.inject.Inject
import javax.inject.Singleton

/**
 * OkHttp Interceptor that adds JWT authentication token to requests.
 *
 * This interceptor automatically adds the Bearer token to the Authorization header
 * for all API requests that require authentication. It retrieves the token from
 * the TokenManager's DataStore.
 *
 * @property tokenManager The token manager for retrieving stored authentication tokens
 */
@Singleton
class AuthInterceptor @Inject constructor(
    private val tokenManager: TokenManager
) : Interceptor {

    /**
     * Endpoints that do not require authentication.
     */
    private val publicEndpoints = listOf(
        "auth/register",
        "auth/login",
        "health"
    )

    /**
     * Intercepts the request and adds the authentication token if required.
     *
     * @param chain The interceptor chain
     * @return The response from the server
     */
    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        val requestUrl = originalRequest.url.toString()

        // Check if this is a public endpoint that doesn't need auth
        val isPublicEndpoint = publicEndpoints.any { requestUrl.contains(it) }

        if (isPublicEndpoint) {
            return chain.proceed(originalRequest)
        }

        // Get the token from DataStore (blocking call, as OkHttp interceptors are synchronous)
        val token = runBlocking {
            tokenManager.getAccessToken().first()
        }

        // If we have a token, add it to the request
        return if (!token.isNullOrEmpty()) {
            val newRequest = originalRequest.newBuilder()
                .addHeader("Authorization", "Bearer $token")
                .build()
            chain.proceed(newRequest)
        } else {
            chain.proceed(originalRequest)
        }
    }
}
