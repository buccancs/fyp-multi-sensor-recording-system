package com.multisensor.recording.di

import android.content.Context
import com.multisensor.recording.recording.CameraRecorder
import com.multisensor.recording.recording.ShimmerRecorder
import com.multisensor.recording.recording.ThermalRecorder
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.util.Logger
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

/**
 * Main Hilt module for dependency injection
 * Provides all the core dependencies needed by the app
 */
@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    
    // Note: The classes with @Inject constructors will be provided automatically by Hilt
    // This module is here to provide any additional dependencies or override defaults if needed
    
    // If any of the @Inject constructors require specific configuration,
    // we can provide them here. For now, Hilt will handle the automatic injection.
}