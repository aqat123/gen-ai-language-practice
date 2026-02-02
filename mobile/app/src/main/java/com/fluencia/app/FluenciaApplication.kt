package com.fluencia.app

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

/**
 * Main Application class for the FluencIA language learning app.
 *
 * This class is annotated with @HiltAndroidApp to enable Hilt dependency
 * injection throughout the application.
 */
@HiltAndroidApp
class FluenciaApplication : Application() {
    
    override fun onCreate() {
        super.onCreate()
        // Application-level initialization can be done here
    }
}
