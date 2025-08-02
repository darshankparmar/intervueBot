import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Chip,
  LinearProgress,
  Alert,
  CircularProgress,
  Paper,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Button,
} from '@mui/material';
import { motion } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import {
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Clock,
  User,
  Mail,
  Briefcase,
  Award,
  Target,
  Star,
  ThumbsUp,
  ThumbsDown,
} from 'lucide-react';
import InterviewService, { InterviewReport } from '../services/api';

const ReportPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  
  const [report, setReport] = useState<InterviewReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (sessionId) {
      loadReport();
    }
  }, [sessionId]);

  const loadReport = async () => {
    if (!sessionId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const reportData = await InterviewService.getInterviewReport(sessionId);
      setReport(reportData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load report');
    } finally {
      setLoading(false);
    }
  };

  const getHiringRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case 'hire':
        return 'success';
      case 'consider':
        return 'warning';
      case 'reject':
        return 'error';
      default:
        return 'default';
    }
  };

  const getHiringRecommendationIcon = (recommendation: string) => {
    switch (recommendation) {
      case 'hire':
        return <ThumbsUp size={20} />;
      case 'consider':
        return <AlertCircle size={20} />;
      case 'reject':
        return <ThumbsDown size={20} />;
      default:
        return <Star size={20} />;
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box textAlign="center">
          <CircularProgress size={60} sx={{ mb: 2 }} />
          <Typography variant="h6">Loading interview report...</Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  if (!report) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="warning">No report data available</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Header */}
        <Box textAlign="center" mb={4}>
          <Typography variant="h3" gutterBottom sx={{ fontWeight: 700 }}>
            Interview Report
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Comprehensive evaluation and hiring recommendation
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 4 }}>
          {/* Candidate Information */}
          <Box sx={{ flex: { xs: '1', md: '0 0 33.333%' } }}>
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <Card sx={{ background: 'rgba(255, 255, 255, 0.9)' }}>
                <CardContent>
                  <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                    Candidate Information
                  </Typography>
                  
                  <Box sx={{ mt: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <User size={20} style={{ marginRight: 8 }} />
                      <Typography variant="body1" sx={{ fontWeight: 600 }}>
                        {report.candidate.name}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Mail size={20} style={{ marginRight: 8 }} />
                      <Typography variant="body2" color="text.secondary">
                        {report.candidate.email}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Briefcase size={20} style={{ marginRight: 8 }} />
                      <Typography variant="body2" color="text.secondary">
                        {report.position}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Award size={20} style={{ marginRight: 8 }} />
                      <Typography variant="body2" color="text.secondary">
                        {report.candidate.experience_level} • {report.candidate.interview_type}
                      </Typography>
                    </Box>
                  </Box>

                  <Divider sx={{ my: 3 }} />

                  <Typography variant="h6" gutterBottom>
                    Interview Statistics
                  </Typography>
                  
                  <Box sx={{ mt: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Questions Asked</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {report.total_questions}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Responses Received</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {report.total_responses}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Avg Response Time</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {Math.round(report.average_response_time)}s
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Interview Duration</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {Math.round(report.interview_duration)}m
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Box>

          {/* Main Report Content */}
          <Box sx={{ flex: { xs: '1', md: '0 0 66.666%' } }}>
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              {/* Overall Score */}
              <Card sx={{ background: 'rgba(255, 255, 255, 0.9)', mb: 3 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                    <TrendingUp size={32} color="#6366f1" style={{ marginRight: 12 }} />
                    <Box>
                      <Typography variant="h5" sx={{ fontWeight: 600 }}>
                        Overall Score
                      </Typography>
                      <Typography variant="h3" sx={{ fontWeight: 700, color: 'primary.main' }}>
                        {report.overall_score}/10
                      </Typography>
                    </Box>
                  </Box>
                  
                  <LinearProgress
                    variant="determinate"
                    value={report.overall_score * 10}
                    sx={{ height: 12, borderRadius: 6 }}
                  />
                </CardContent>
              </Card>

              {/* Detailed Scores */}
              <Card sx={{ background: 'rgba(255, 255, 255, 0.9)', mb: 3 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    Detailed Assessment
                  </Typography>
                  
                  <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 3 }}>
                    {report.technical_score && (
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Technical Skills
                        </Typography>
                        <Typography variant="h4" sx={{ fontWeight: 600 }}>
                          {report.technical_score}/10
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={report.technical_score * 10}
                          sx={{ mt: 1 }}
                        />
                      </Box>
                    )}
                    
                    {report.communication_score && (
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Communication
                        </Typography>
                        <Typography variant="h4" sx={{ fontWeight: 600 }}>
                          {report.communication_score}/10
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={report.communication_score * 10}
                          sx={{ mt: 1 }}
                        />
                      </Box>
                    )}
                    
                    {report.problem_solving_score && (
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Problem Solving
                        </Typography>
                        <Typography variant="h4" sx={{ fontWeight: 600 }}>
                          {report.problem_solving_score}/10
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={report.problem_solving_score * 10}
                          sx={{ mt: 1 }}
                        />
                      </Box>
                    )}
                    
                    {report.cultural_fit_score && (
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Cultural Fit
                        </Typography>
                        <Typography variant="h4" sx={{ fontWeight: 600 }}>
                          {report.cultural_fit_score}/10
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={report.cultural_fit_score * 10}
                          sx={{ mt: 1 }}
                        />
                      </Box>
                    )}
                  </Box>
                </CardContent>
              </Card>

              {/* Hiring Recommendation */}
              <Card sx={{ background: 'rgba(255, 255, 255, 0.9)', mb: 3 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    {getHiringRecommendationIcon(report.hiring_recommendation)}
                    <Typography variant="h5" sx={{ fontWeight: 600, ml: 1 }}>
                      Hiring Recommendation
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <Chip
                      label={report.hiring_recommendation.toUpperCase()}
                      color={getHiringRecommendationColor(report.hiring_recommendation)}
                      sx={{ fontWeight: 600 }}
                    />
                    <Typography variant="body2" color="text.secondary">
                      Confidence: {Math.round(report.confidence_level * 100)}%
                    </Typography>
                  </Box>
                  
                  <Typography variant="body1" sx={{ lineHeight: 1.6 }}>
                    {report.detailed_feedback}
                  </Typography>
                </CardContent>
              </Card>

              {/* Strengths and Areas for Improvement */}
              <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 3 }}>
                <Box sx={{ flex: 1 }}>
                  <Card sx={{ background: 'rgba(255, 255, 255, 0.9)' }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: 'success.main' }}>
                        Strengths
                      </Typography>
                      <List dense>
                        {report.strengths.map((strength, index) => (
                          <ListItem key={index} sx={{ py: 0.5 }}>
                            <ListItemIcon sx={{ minWidth: 32 }}>
                              <CheckCircle size={16} color="#10b981" />
                            </ListItemIcon>
                            <ListItemText primary={strength} />
                          </ListItem>
                        ))}
                      </List>
                    </CardContent>
                  </Card>
                </Box>
                
                <Box sx={{ flex: 1 }}>
                  <Card sx={{ background: 'rgba(255, 255, 255, 0.9)' }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: 'warning.main' }}>
                        Areas for Improvement
                      </Typography>
                      <List dense>
                        {report.areas_for_improvement.map((area, index) => (
                          <ListItem key={index} sx={{ py: 0.5 }}>
                            <ListItemIcon sx={{ minWidth: 32 }}>
                              <AlertCircle size={16} color="#f59e0b" />
                            </ListItemIcon>
                            <ListItemText primary={area} />
                          </ListItem>
                        ))}
                      </List>
                    </CardContent>
                  </Card>
                </Box>
              </Box>
            </motion.div>
          </Box>
        </Box>

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4, gap: 2 }}>
          <Button
            variant="contained"
            size="large"
            onClick={() => navigate('/')}
            sx={{ px: 4 }}
          >
            Start New Interview
          </Button>
        </Box>
      </motion.div>
    </Container>
  );
};

export default ReportPage; 