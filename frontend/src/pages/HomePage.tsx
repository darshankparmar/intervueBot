import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
} from '@mui/material';
import { motion } from 'framer-motion';
import {
  User,
  Mail,
  Briefcase,
  Award,
  Clock,
  CheckCircle,
  AlertCircle,
  FileText,
  Upload,
} from 'lucide-react';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useNavigate } from 'react-router-dom';

import { InterviewService, InterviewCreate, CandidateProfile } from '../services/api';

import FileUpload from '../components/FileUpload';

// Form data type without files (files are handled separately)
interface InterviewFormData {
  candidate: {
    name: string;
    email: string;
    position: string;
    experience_level: 'junior' | 'mid-level' | 'senior' | 'lead';
    interview_type: 'technical' | 'behavioral' | 'mixed' | 'leadership';
  };
  duration_minutes: number;
}

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  fileType: 'resume' | 'cv' | 'cover_letter';
  content: string;
  status: 'uploading' | 'success' | 'error';
  error?: string;
}

// Validation schema
const schema = yup.object().shape({
  candidate: yup.object().shape({
    name: yup.string().required('Name is required'),
    email: yup.string().email('Invalid email').required('Email is required'),
    position: yup.string().required('Position is required'),
    experience_level: yup.string().oneOf(['junior', 'mid-level', 'senior', 'lead']).required('Experience level is required'),
    interview_type: yup.string().oneOf(['technical', 'behavioral', 'mixed', 'leadership']).required('Interview type is required'),
    // Remove files validation from schema since we handle it manually in onSubmit
  }),
  duration_minutes: yup.number().min(30).max(120).required('Duration is required'),
});

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);

  const {
    control,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<InterviewFormData>({
    resolver: yupResolver(schema),
    defaultValues: {
      candidate: {
        name: '',
        email: '',
        position: '',
        experience_level: 'mid-level',
        interview_type: 'technical',
      },
      duration_minutes: 60,
    },
  });

  const onSubmit = async (data: InterviewFormData) => {
    try {
      setLoading(true);
      setError(null);

      // Convert uploaded files to the format expected by the API
      const filesForAPI = uploadedFiles
        .filter(file => file.status === 'success')
        .map(file => ({
          name: file.name,
          type: file.fileType,
          size: file.size,
          content: file.content,
        }));

      if (filesForAPI.length === 0) {
        setError('Please upload at least one valid file');
        return;
      }

      // Update the form data with uploaded files
      const interviewData: InterviewCreate = {
        ...data,
        candidate: {
          ...data.candidate,
          files: filesForAPI,
        },
      };

      // Start the interview
      const response = await InterviewService.startInterview(interviewData);
      
      // Navigate to interview page with session ID
      navigate(`/interview/${response.session_id}`);
      
    } catch (err: any) {
      setError(err.message || 'Failed to start interview');
    } finally {
      setLoading(false);
    }
  };

  const handleFilesChange = (files: UploadedFile[]) => {
    setUploadedFiles(files);
  };

  const features = [
    {
      icon: <User size={24} color="#6366f1" />,
      title: 'AI-Powered Interviews',
      description: 'Advanced AI agents conduct intelligent, adaptive interviews based on candidate responses and resume analysis.',
    },
    {
      icon: <CheckCircle size={24} color="#10b981" />,
      title: 'Real-time Evaluation',
      description: 'Get instant feedback and scoring on technical skills, communication, and problem-solving abilities.',
    },
    {
      icon: <FileText size={24} color="#f59e0b" />,
      title: 'Resume Analysis',
      description: 'Automated parsing and analysis of resumes, CVs, and cover letters to extract relevant information.',
    },
    {
      icon: <Award size={24} color="#8b5cf6" />,
      title: 'Comprehensive Reports',
      description: 'Detailed interview reports with hiring recommendations, skill gaps, and improvement suggestions.',
    },
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Header */}
        <Box textAlign="center" sx={{ mb: 6 }}>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <Typography
              variant="h2"
              sx={{
                fontWeight: 700,
                background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                mb: 2,
              }}
            >
              IntervueBot
            </Typography>
            <Typography variant="h5" color="text.secondary" sx={{ mb: 4 }}>
              AI-Powered Interview Platform
            </Typography>
          </motion.div>
        </Box>

        <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 4 }}>
          {/* Features Section */}
          <Box sx={{ flex: { xs: '1', md: '0 0 33.333%' } }}>
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <Card sx={{ background: 'rgba(255, 255, 255, 0.9)', height: '100%' }}>
                <CardContent>
                  <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                    Key Features
                  </Typography>
                  
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                    {features.map((feature, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.4, delay: 0.3 + index * 0.1 }}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                          <Box sx={{ color: 'primary.main', mt: 0.5 }}>
                            {feature.icon}
                          </Box>
                          <Box>
                            <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                              {feature.title}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {feature.description}
                            </Typography>
                          </Box>
                        </Box>
                      </motion.div>
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Box>

          {/* Interview Form */}
          <Box sx={{ flex: { xs: '1', md: '0 0 66.666%' } }}>
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <Card sx={{ background: 'rgba(255, 255, 255, 0.9)' }}>
                <CardContent>
                  <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, mb: 4 }}>
                    Start Your Interview
                  </Typography>

                  {error && (
                    <Alert severity="error" sx={{ mb: 3 }}>
                      {error}
                    </Alert>
                  )}

                  <form onSubmit={handleSubmit(onSubmit)}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                      {/* Basic Information */}
                      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 3 }}>
                        <Box sx={{ flex: 1 }}>
                          <Controller
                            name="candidate.name"
                            control={control}
                            render={({ field }) => (
                              <TextField
                                {...field}
                                label="Full Name"
                                fullWidth
                                error={!!errors.candidate?.name}
                                helperText={errors.candidate?.name?.message}
                                sx={{ mb: 2 }}
                              />
                            )}
                          />
                        </Box>

                        <Box sx={{ flex: 1 }}>
                          <Controller
                            name="candidate.email"
                            control={control}
                            render={({ field }) => (
                              <TextField
                                {...field}
                                label="Email Address"
                                type="email"
                                fullWidth
                                error={!!errors.candidate?.email}
                                helperText={errors.candidate?.email?.message}
                                sx={{ mb: 2 }}
                              />
                            )}
                          />
                        </Box>
                      </Box>

                      <Box>
                        <Controller
                          name="candidate.position"
                          control={control}
                          render={({ field }) => (
                            <TextField
                              {...field}
                              label="Position Applied For"
                              fullWidth
                              error={!!errors.candidate?.position}
                              helperText={errors.candidate?.position?.message}
                              sx={{ mb: 2 }}
                            />
                          )}
                        />
                      </Box>

                      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 3 }}>
                        <Box sx={{ flex: 1 }}>
                          <Controller
                            name="candidate.experience_level"
                            control={control}
                            render={({ field }) => (
                              <FormControl fullWidth error={!!errors.candidate?.experience_level}>
                                <InputLabel>Experience Level</InputLabel>
                                <Select {...field} label="Experience Level">
                                  <MenuItem value="junior">Junior (0-2 years)</MenuItem>
                                  <MenuItem value="mid-level">Mid-Level (3-5 years)</MenuItem>
                                  <MenuItem value="senior">Senior (6-8 years)</MenuItem>
                                  <MenuItem value="lead">Lead (9+ years)</MenuItem>
                                </Select>
                                {errors.candidate?.experience_level && (
                                  <Typography variant="caption" color="error">
                                    {errors.candidate.experience_level.message}
                                  </Typography>
                                )}
                              </FormControl>
                            )}
                          />
                        </Box>

                        <Box sx={{ flex: 1 }}>
                          <Controller
                            name="candidate.interview_type"
                            control={control}
                            render={({ field }) => (
                              <FormControl fullWidth error={!!errors.candidate?.interview_type}>
                                <InputLabel>Interview Type</InputLabel>
                                <Select {...field} label="Interview Type">
                                  <MenuItem value="technical">Technical</MenuItem>
                                  <MenuItem value="behavioral">Behavioral</MenuItem>
                                  <MenuItem value="mixed">Mixed</MenuItem>
                                  <MenuItem value="leadership">Leadership</MenuItem>
                                </Select>
                                {errors.candidate?.interview_type && (
                                  <Typography variant="caption" color="error">
                                    {errors.candidate.interview_type.message}
                                  </Typography>
                                )}
                              </FormControl>
                            )}
                          />
                        </Box>
                      </Box>

                      <Box>
                        <Controller
                          name="duration_minutes"
                          control={control}
                          render={({ field }) => (
                            <TextField
                              {...field}
                              label="Interview Duration (minutes)"
                              type="number"
                              fullWidth
                              error={!!errors.duration_minutes}
                              helperText={errors.duration_minutes?.message}
                              sx={{ mb: 2 }}
                            />
                          )}
                        />
                      </Box>

                      {/* File Upload Section */}
                      <Box>
                        <FileUpload
                          onFilesChange={handleFilesChange}
                          maxFiles={10}
                          maxSize={10 * 1024 * 1024} // 10MB
                        />
                      </Box>

                      {/* Submit Button */}
                      <Box>
                        <Button
                          type="submit"
                          variant="contained"
                          size="large"
                          fullWidth
                          disabled={loading}
                          sx={{
                            py: 2,
                            fontSize: '1.1rem',
                            fontWeight: 600,
                            background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                            '&:hover': {
                              background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
                            },
                          }}
                        >
                          {loading ? (
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <CircularProgress size={20} color="inherit" />
                              Starting Interview...
                            </Box>
                          ) : (
                            'Start Interview'
                          )}
                        </Button>
                      </Box>
                    </Box>
                  </form>
                </CardContent>
              </Card>
            </motion.div>
          </Box>
        </Box>
      </motion.div>
    </Container>
  );
};

export default HomePage; 