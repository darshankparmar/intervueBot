import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  TextField,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  Chip,
  LinearProgress,
} from '@mui/material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  Upload,
  FileText,
  User,
  Mail,
  Briefcase,
  Clock,
  CheckCircle,
  AlertCircle,
} from 'lucide-react';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import InterviewService, { FileService, FileInfo, FileReference } from '../services/api';

// Form validation schema
const schema = yup.object().shape({
  name: yup.string().required('Name is required'),
  email: yup.string().email('Valid email is required').required('Email is required'),
  position: yup.string().required('Position is required'),
  experience_level: yup.string().oneOf(['junior', 'mid-level', 'senior', 'lead']).required('Experience level is required'),
  interview_type: yup.string().oneOf(['technical', 'behavioral', 'mixed', 'leadership']).required('Interview type is required'),
  duration_minutes: yup.number().min(15, 'Minimum 15 minutes').max(120, 'Maximum 120 minutes').required('Duration is required'),
});

interface InterviewFormData {
  name: string;
  email: string;
  position: string;
  experience_level: 'junior' | 'mid-level' | 'senior' | 'lead';
  interview_type: 'technical' | 'behavioral' | 'mixed' | 'leadership';
  duration_minutes: number;
}

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedFiles, setUploadedFiles] = useState<FileInfo[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const {
    control,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<InterviewFormData>({
    resolver: yupResolver(schema),
    defaultValues: {
      experience_level: 'mid-level',
      interview_type: 'technical',
      duration_minutes: 60,
    },
  });

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    setUploadProgress(0);
    setError(null);
    setSuccess(null);

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // Upload files
      const uploadResponse = await FileService.uploadFiles(Array.from(files));
      
      clearInterval(progressInterval);
      setUploadProgress(100);

      if (uploadResponse.status === 'success' || uploadResponse.status === 'partial_success') {
        setUploadedFiles(uploadResponse.files);
        setSuccess(uploadResponse.message);
        
        if (uploadResponse.errors.length > 0) {
          setError(`Some files had issues: ${uploadResponse.errors.join(', ')}`);
        }
      } else {
        setError('File upload failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'File upload failed');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(file => file.file_id !== fileId));
  };

  const onSubmit = async (data: InterviewFormData) => {
    if (uploadedFiles.length === 0) {
      setError('Please upload at least one file before starting the interview');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      // Convert uploaded files to file references
      const fileReferences: FileReference[] = uploadedFiles.map(file => ({
        file_id: file.file_id,
        filename: file.filename,
        file_type: file.file_type as 'resume' | 'cv' | 'cover_letter'
      }));

      // Start interview with file references
      const response = await InterviewService.startInterview({
        candidate: {
          ...data,
          files: fileReferences,
        },
        duration_minutes: data.duration_minutes,
      });

      setSuccess('Interview started successfully!');
      
      // Navigate to interview page after a short delay
      setTimeout(() => {
        navigate(`/interview/${response.session_id}`);
      }, 1500);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start interview');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Header */}
        <Box textAlign="center" sx={{ mb: 6 }}>
          <Typography variant="h2" gutterBottom sx={{ fontWeight: 700, color: 'primary.main' }}>
            IntervueBot 🤖
          </Typography>
          <Typography variant="h5" color="text.secondary" sx={{ mb: 2 }}>
            AI-Powered Interview Experience
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 600, mx: 'auto' }}>
            Upload your resume and start your AI interview. Our intelligent system will adapt questions based on your background and provide comprehensive feedback.
          </Typography>
        </Box>

        {/* File Upload Section */}
        <Card sx={{ mb: 4, background: 'rgba(255, 255, 255, 0.9)' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Upload size={20} />
              Upload Documents
            </Typography>
            
            <Box sx={{ mb: 3 }}>
              <input
                accept=".pdf,.doc,.docx,.txt,.rtf"
                style={{ display: 'none' }}
                id="file-upload"
                multiple
                type="file"
                onChange={handleFileUpload}
                disabled={uploading}
              />
              <label htmlFor="file-upload">
                <Button
                  variant="outlined"
                  component="span"
                  startIcon={<Upload />}
                  disabled={uploading}
                  sx={{ mb: 2 }}
                >
                  Choose Files
                </Button>
              </label>
              
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Supported formats: PDF, DOC, DOCX, TXT, RTF (Max 10MB per file)
              </Typography>

              {uploading && (
                <Box sx={{ width: '100%', mb: 2 }}>
                  <LinearProgress variant="determinate" value={uploadProgress} />
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Uploading... {uploadProgress}%
                  </Typography>
                </Box>
              )}

              {uploadedFiles.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Uploaded Files:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {uploadedFiles.map((file) => (
                      <Chip
                        key={file.file_id}
                        icon={<FileText size={16} />}
                        label={file.filename}
                        onDelete={() => removeFile(file.file_id)}
                        color="primary"
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </Box>
              )}
            </Box>
          </CardContent>
        </Card>

        {/* Interview Form */}
        <Card sx={{ background: 'rgba(255, 255, 255, 0.9)' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <User size={20} />
              Interview Details
            </Typography>

            <form onSubmit={handleSubmit(onSubmit)}>
              <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, gap: 3 }}>
                {/* Name */}
                <Box>
                  <Controller
                    name="name"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        fullWidth
                        label="Full Name"
                        error={!!errors.name}
                        helperText={errors.name?.message}
                        InputProps={{
                          startAdornment: <User size={20} style={{ marginRight: 8, color: 'gray' }} />,
                        }}
                      />
                    )}
                  />
                </Box>

                {/* Email */}
                <Box>
                  <Controller
                    name="email"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        fullWidth
                        label="Email Address"
                        type="email"
                        error={!!errors.email}
                        helperText={errors.email?.message}
                        InputProps={{
                          startAdornment: <Mail size={20} style={{ marginRight: 8, color: 'gray' }} />,
                        }}
                      />
                    )}
                  />
                </Box>

                {/* Position */}
                <Box>
                  <Controller
                    name="position"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        fullWidth
                        label="Position Applied For"
                        error={!!errors.position}
                        helperText={errors.position?.message}
                        InputProps={{
                          startAdornment: <Briefcase size={20} style={{ marginRight: 8, color: 'gray' }} />,
                        }}
                      />
                    )}
                  />
                </Box>

                {/* Experience Level */}
                <Box>
                  <Controller
                    name="experience_level"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        fullWidth
                        select
                        label="Experience Level"
                        error={!!errors.experience_level}
                        helperText={errors.experience_level?.message}
                      >
                        <option value="junior">Junior (0-2 years)</option>
                        <option value="mid-level">Mid-Level (2-5 years)</option>
                        <option value="senior">Senior (5-8 years)</option>
                        <option value="lead">Lead (8+ years)</option>
                      </TextField>
                    )}
                  />
                </Box>

                {/* Interview Type */}
                <Box>
                  <Controller
                    name="interview_type"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        fullWidth
                        select
                        label="Interview Type"
                        error={!!errors.interview_type}
                        helperText={errors.interview_type?.message}
                      >
                        <option value="technical">Technical</option>
                        <option value="behavioral">Behavioral</option>
                        <option value="mixed">Mixed</option>
                        <option value="leadership">Leadership</option>
                      </TextField>
                    )}
                  />
                </Box>

                {/* Duration */}
                <Box>
                  <Controller
                    name="duration_minutes"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        fullWidth
                        label="Duration (minutes)"
                        type="number"
                        error={!!errors.duration_minutes}
                        helperText={errors.duration_minutes?.message}
                        InputProps={{
                          startAdornment: <Clock size={20} style={{ marginRight: 8, color: 'gray' }} />,
                        }}
                      />
                    )}
                  />
                </Box>

                {/* Submit Button */}
                <Box sx={{ gridColumn: { xs: '1', sm: '1 / -1' } }}>
                  <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    fullWidth
                    disabled={loading || uploading || uploadedFiles.length === 0}
                    startIcon={loading ? <CircularProgress size={20} /> : <CheckCircle size={20} />}
                    sx={{ py: 1.5 }}
                  >
                    {loading ? 'Starting Interview...' : 'Start Interview'}
                  </Button>
                </Box>
              </Box>
            </form>
          </CardContent>
        </Card>

        {/* Alerts */}
        {error && (
          <Alert severity="error" sx={{ mt: 3 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mt: 3 }} onClose={() => setSuccess(null)}>
            {success}
          </Alert>
        )}
      </motion.div>
    </Container>
  );
};

export default HomePage; 