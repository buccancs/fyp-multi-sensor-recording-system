package com.multisensor.recording.di

import com.multisensor.recording.controllers.ControllerConnectionManager
import com.multisensor.recording.controllers.PcControllerConnectionManager
import com.multisensor.recording.streaming.NetworkPreviewStreamer
import com.multisensor.recording.streaming.PreviewStreamingInterface
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class AppModule {

    @Binds
    @Singleton
    abstract fun bindControllerConnectionManager(
        pcControllerConnectionManager: PcControllerConnectionManager
    ): ControllerConnectionManager

    @Binds
    @Singleton
    abstract fun bindPreviewStreamingInterface(
        networkPreviewStreamer: NetworkPreviewStreamer
    ): PreviewStreamingInterface
}
