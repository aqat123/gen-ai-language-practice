package com.fluencia.app.di

import com.fluencia.app.BuildConfig
import com.fluencia.app.data.api.AuthInterceptor
import com.fluencia.app.data.api.FluenciaApiService
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
import javax.inject.Singleton

/**
 * Hilt module for providing network-related dependencies.
 *
 * This module configures and provides Retrofit, OkHttp, and the API service
 * for dependency injection throughout the application.
 */
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    /**
     * Provides the HTTP logging interceptor for debugging.
     *
     * @return Configured HttpLoggingInterceptor
     */
    @Provides
    @Singleton
    fun provideLoggingInterceptor(): HttpLoggingInterceptor {
        return HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) {
                HttpLoggingInterceptor.Level.BODY
            } else {
                HttpLoggingInterceptor.Level.NONE
            }
        }
    }

    /**
     * Provides the OkHttpClient with interceptors configured.
     *
     * @param authInterceptor The authentication interceptor for adding JWT tokens
     * @param loggingInterceptor The logging interceptor for debugging
     * @return Configured OkHttpClient
     */
    @Provides
    @Singleton
    fun provideOkHttpClient(
        authInterceptor: AuthInterceptor,
        loggingInterceptor: HttpLoggingInterceptor
    ): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(loggingInterceptor)
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.SECONDS)
            .writeTimeout(60, TimeUnit.SECONDS)
            .build()
    }

    /**
     * Provides the Retrofit instance configured for the API.
     *
     * @param okHttpClient The configured OkHttpClient
     * @return Configured Retrofit instance
     */
    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl(BuildConfig.API_BASE_URL + "/")
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    /**
     * Provides the FluencIA API service.
     *
     * @param retrofit The configured Retrofit instance
     * @return FluenciaApiService implementation
     */
    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): FluenciaApiService {
        return retrofit.create(FluenciaApiService::class.java)
    }
}
