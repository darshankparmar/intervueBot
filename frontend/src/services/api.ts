import axios, { AxiosResponse } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// API client with default configuration
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Types for API requests and responses
export interface FileReference {
  file_id: string;
  filename: string;
  file_type: 'resume' | 'cv' | 'cover_letter';
}

export interface FileInfo {
  file_id: string;
  filename: string;
  file_type: 'resume' | 'cv' | 'cover_letter';
  size: number;
  uploaded_at: string;
}

export interface FileUploadResponse {
  status: string;
  message: string;
  files: FileInfo[];
  errors: string[];
}

export interface CandidateProfile {
  name: string;
  email: string;
  position: string;
  experience_level: 'junior' | 'mid-level' | 'senior' | 'lead';
  interview_type: 'technical' | 'behavioral' | 'mixed' | 'leadership';
  files: FileReference[];
}

export interface ResumeAnalysis {
  extracted_skills: string[];
  experience_years: number;
  education?: string;
  current_company?: string;
  previous_companies: string[];
  projects: any[];
  certifications: string[];
  languages: string[];
  technologies: string[];
  confidence_score: number;
}

export interface CandidateProfileWithAnalysis extends CandidateProfile {
  resume_analysis?: ResumeAnalysis;
}

export interface InterviewCreate {
  candidate: CandidateProfile;
  duration_minutes: number;
}

export interface InterviewResponse {
  session_id: string;
  candidate: CandidateProfileWithAnalysis;
  position: string;
  status: string;
  started_at: string;
  current_question_index: number;
  total_questions_asked: number;
  average_score: number;
}

export interface Question {
  id: string;
  text: string;
  category: string;
  difficulty: 'easy' | 'medium' | 'hard';
  expected_duration: number;
  context?: any;
  follow_up_hints: string[];
}

export interface QuestionResponse {
  question: Question;
  session_id: string;
  question_number: number;
  time_limit: number;
  context?: any;
}

export interface ResponseSubmit {
  question_id: string;
  answer: string;
  time_taken: number;
}

export interface ResponseEvaluation {
  overall_score: number;
  technical_accuracy: number;
  communication_clarity: number;
  problem_solving_approach: number;
  experience_relevance: number;
  strengths: string[];
  areas_for_improvement: string[];
  suggestions: string[];
  suggested_difficulty: 'easy' | 'medium' | 'hard';
  follow_up_questions: string[];
  skill_gaps: string[];
}

export interface SubmitResponseResult {
  status: string;
  message: string;
  evaluation: ResponseEvaluation;
  next_steps: string;
}

export interface FinalizeResult {
  status: string;
  message: string;
  session_id: string;
  report_summary: {
    overall_score: number;
    hiring_recommendation: 'hire' | 'consider' | 'reject';
    confidence_level: number;
    total_questions: number;
    total_responses: number;
    average_response_time: number;
  };
}

export interface InterviewReport {
  session_id: string;
  candidate: CandidateProfileWithAnalysis;
  position: string;
  overall_score: number;
  technical_score?: number;
  behavioral_score?: number;
  communication_score?: number;
  problem_solving_score?: number;
  cultural_fit_score?: number;
  strengths: string[];
  areas_for_improvement: string[];
  skill_gaps: string[];
  recommendations: string[];
  total_questions: number;
  total_responses: number;
  average_response_time: number;
  difficulty_progression: any[];
  hiring_recommendation: 'hire' | 'consider' | 'reject';
  confidence_level: number;
  detailed_feedback: string;
  generated_at: string;
  interview_duration: number;
}

// API service class
export class InterviewService {
  // Start a new interview session
  static async startInterview(data: InterviewCreate): Promise<InterviewResponse> {
    try {
      const response: AxiosResponse<InterviewResponse> = await apiClient.post(
        '/api/v1/interviews/start',
        data
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to start interview');
    }
  }

  // Get the next question for an interview session
  static async getNextQuestion(sessionId: string): Promise<QuestionResponse> {
    try {
      const response: AxiosResponse<QuestionResponse> = await apiClient.get(
        `/api/v1/interviews/${sessionId}/next-question`
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to get next question');
    }
  }

  // Submit a response to the current question
  static async submitResponse(
    sessionId: string,
    data: ResponseSubmit
  ): Promise<SubmitResponseResult> {
    try {
      const response: AxiosResponse<SubmitResponseResult> = await apiClient.post(
        `/api/v1/interviews/${sessionId}/respond`,
        data
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to submit response');
    }
  }

  // Finalize the interview
  static async finalizeInterview(sessionId: string): Promise<FinalizeResult> {
    try {
      const response: AxiosResponse<FinalizeResult> = await apiClient.post(
        `/api/v1/interviews/${sessionId}/finalize`
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to finalize interview');
    }
  }

  // Get the interview report
  static async getInterviewReport(sessionId: string): Promise<InterviewReport> {
    try {
      const response: AxiosResponse<InterviewReport> = await apiClient.get(
        `/api/v1/interviews/${sessionId}/report`
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to get interview report');
    }
  }

  // Health check
  static async healthCheck(): Promise<any> {
    try {
      const response = await apiClient.get('/');
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to connect to server');
    }
  }

  // Error handling utility
  private static handleError(error: any, defaultMessage: string): Error {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.message || defaultMessage;
      return new Error(message);
    } else if (error.request) {
      // Request was made but no response received
      return new Error('No response from server. Please check your connection.');
    } else {
      // Something else happened
      return new Error(error.message || defaultMessage);
    }
  }
}

export class FileService {
  /**
   * Upload files for interview preparation.
   */
  static async uploadFiles(files: File[]): Promise<FileUploadResponse> {
    try {
      const formData = new FormData();
      files.forEach((file) => {
        formData.append('files', file);
      });

      const response = await apiClient.post<FileUploadResponse>('/api/v1/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to upload files');
    }
  }

  /**
   * Get file information by ID.
   */
  static async getFileInfo(fileId: string): Promise<FileInfo> {
    try {
      const response = await apiClient.get<FileInfo>(`/api/v1/files/${fileId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to get file info');
    }
  }

  /**
   * Delete a file by ID.
   */
  static async deleteFile(fileId: string): Promise<void> {
    try {
      await apiClient.delete(`/api/v1/files/${fileId}`);
    } catch (error) {
      throw this.handleError(error, 'Failed to delete file');
    }
  }

  private static handleError(error: any, defaultMessage: string): Error {
    if (error.response?.data?.detail) {
      return new Error(error.response.data.detail);
    }
    return new Error(defaultMessage);
  }
}

// Export default instance
export default InterviewService; 