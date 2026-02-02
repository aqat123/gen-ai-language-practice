package com.fluencia.app.ui.screens.phonetics

import android.content.Context
import android.media.MediaRecorder
import android.os.Build
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.fluencia.app.data.model.PhoneticsEvaluationResponse
import com.fluencia.app.data.repository.LearningRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.io.File
import javax.inject.Inject

/**
 * UI state for the phonetics screen.
 */
sealed class PhoneticsUiState {
    /** Loading state */
    object Loading : PhoneticsUiState()
    
    /** Practice state */
    data class Practice(
        val targetPhrase: String,
        val isRecording: Boolean = false,
        val hasRecording: Boolean = false,
        val evaluation: PhoneticsEvaluationResponse? = null
    ) : PhoneticsUiState()
    
    /** Evaluating state */
    object Evaluating : PhoneticsUiState()
    
    /** Error state */
    data class Error(val message: String) : PhoneticsUiState()
}

/**
 * ViewModel for the phonetics screen.
 *
 * Manages pronunciation practice including audio recording and evaluation.
 *
 * @property learningRepository Repository for learning operations
 * @property context Application context for file operations
 */
@HiltViewModel
class PhoneticsViewModel @Inject constructor(
    private val learningRepository: LearningRepository,
    @ApplicationContext private val context: Context
) : ViewModel() {

    private val _uiState = MutableStateFlow<PhoneticsUiState>(PhoneticsUiState.Loading)
    
    /** Current UI state */
    val uiState: StateFlow<PhoneticsUiState> = _uiState.asStateFlow()
    
    private var mediaRecorder: MediaRecorder? = null
    private var audioFile: File? = null
    private var currentPhrase: String = ""

    /**
     * Load a new practice phrase.
     */
    fun loadPhrase() {
        viewModelScope.launch {
            _uiState.value = PhoneticsUiState.Loading
            
            // Clean up previous recording
            audioFile?.delete()
            audioFile = null
            
            val result = learningRepository.getPhoneticsPracticePhrase()
            
            result.fold(
                onSuccess = { response ->
                    currentPhrase = response.targetPhrase
                    _uiState.value = PhoneticsUiState.Practice(
                        targetPhrase = response.targetPhrase
                    )
                },
                onFailure = { exception ->
                    _uiState.value = PhoneticsUiState.Error(
                        exception.message ?: "Failed to load phrase"
                    )
                }
            )
        }
    }

    /**
     * Start audio recording.
     */
    fun startRecording() {
        try {
            audioFile = File(context.cacheDir, "recording_${System.currentTimeMillis()}.m4a")
            
            mediaRecorder = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                MediaRecorder(context)
            } else {
                @Suppress("DEPRECATION")
                MediaRecorder()
            }.apply {
                setAudioSource(MediaRecorder.AudioSource.MIC)
                setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
                setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
                setAudioEncodingBitRate(128000)
                setAudioSamplingRate(44100)
                setOutputFile(audioFile?.absolutePath)
                prepare()
                start()
            }
            
            updatePracticeState { it.copy(isRecording = true, hasRecording = false, evaluation = null) }
        } catch (e: Exception) {
            _uiState.value = PhoneticsUiState.Error("Failed to start recording: ${e.message}")
        }
    }

    /**
     * Stop audio recording.
     */
    fun stopRecording() {
        try {
            mediaRecorder?.apply {
                stop()
                release()
            }
            mediaRecorder = null
            
            updatePracticeState { it.copy(isRecording = false, hasRecording = true) }
        } catch (e: Exception) {
            _uiState.value = PhoneticsUiState.Error("Failed to stop recording: ${e.message}")
        }
    }

    /**
     * Submit recording for pronunciation evaluation.
     */
    fun validatePronunciation() {
        val file = audioFile ?: return
        
        viewModelScope.launch {
            _uiState.value = PhoneticsUiState.Evaluating
            
            val result = learningRepository.evaluatePronunciation(currentPhrase, file)
            
            result.fold(
                onSuccess = { response ->
                    _uiState.value = PhoneticsUiState.Practice(
                        targetPhrase = currentPhrase,
                        isRecording = false,
                        hasRecording = true,
                        evaluation = response
                    )
                },
                onFailure = { exception ->
                    _uiState.value = PhoneticsUiState.Practice(
                        targetPhrase = currentPhrase,
                        isRecording = false,
                        hasRecording = true
                    )
                    // Could show error toast here
                }
            )
        }
    }

    /**
     * Helper to update practice state.
     */
    private fun updatePracticeState(update: (PhoneticsUiState.Practice) -> PhoneticsUiState.Practice) {
        val current = _uiState.value
        if (current is PhoneticsUiState.Practice) {
            _uiState.value = update(current)
        }
    }

    override fun onCleared() {
        super.onCleared()
        mediaRecorder?.release()
        audioFile?.delete()
    }
}
