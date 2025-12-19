import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
    History, 
    Search, 
    Calendar, 
    Clock, 
    FileText, 
    BarChart3, 
    Trash2, 
    ExternalLink,
    User,
    LogOut,
    Settings,
    Crown
} from 'lucide-react';

interface UserQuestion {
    id: number;
    question_text: string;
    question_type: string;
    similarity_score: number | null;
    match_count: number;
    processing_time: number | null;
    status: string;
    created_at: string;
}

interface UserInfo {
    id: number;
    username: string;
    email: string;
    full_name: string | null;
    is_premium: boolean;
}

const MyPage: React.FC = () => {
    const navigate = useNavigate();
    const [user, setUser] = useState<UserInfo | null>(null);
    const [questions, setQuestions] = useState<UserQuestion[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [totalCount, setTotalCount] = useState(0);
    const [hasMore, setHasMore] = useState(false);

    useEffect(() => {
        // 로그인 확인
        const token = localStorage.getItem('access_token');
        const userInfo = localStorage.getItem('user_info');

        if (!token || !userInfo) {
            navigate('/login');
            return;
        }

        setUser(JSON.parse(userInfo));
        fetchQuestions();
    }, [navigate]);

    const fetchQuestions = async () => {
        const token = localStorage.getItem('access_token');
        
        try {
            setLoading(true);
            const response = await fetch('http://localhost:8006/api/auth/questions', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                setQuestions(data.questions);
                setTotalCount(data.total_count);
                setHasMore(data.has_more);
            } else {
                setError('질문 기록을 불러오는데 실패했습니다.');
            }
        } catch (error) {
            setError('서버 연결에 실패했습니다.');
            console.error('Fetch questions error:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_info');
        navigate('/');
    };

    const deleteQuestion = async (questionId: number) => {
        const token = localStorage.getItem('access_token');
        
        if (!confirm('이 질문 기록을 삭제하시겠습니까?')) {
            return;
        }

        try {
            const response = await fetch(`http://localhost:8006/api/auth/questions/${questionId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                setQuestions(prev => prev.filter(q => q.id !== questionId));
                setTotalCount(prev => prev - 1);
            } else {
                setError('질문 삭제에 실패했습니다.');
            }
        } catch (error) {
            setError('서버 연결에 실패했습니다.');
            console.error('Delete question error:', error);
        }
    };

    const getQuestionTypeText = (type: string) => {
        switch (type) {
            case 'plagiarism_check': return '표절 검사';
            case 'premium_analysis': return '프리미엄 분석';
            case 'general': return '일반 질문';
            default: return type;
        }
    };

    const getQuestionTypeIcon = (type: string) => {
        switch (type) {
            case 'plagiarism_check': return <Search className="h-4 w-4" />;
            case 'premium_analysis': return <BarChart3 className="h-4 w-4" />;
            case 'general': return <FileText className="h-4 w-4" />;
            default: return <FileText className="h-4 w-4" />;
        }
    };

    const getSimilarityColor = (similarity: number | null) => {
        if (!similarity) return 'secondary';
        if (similarity < 15) return 'default';
        if (similarity < 40) return 'destructive';
        return 'destructive';
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                <span className="ml-2">데이터 로딩 중...</span>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
            {/* 헤더 */}
            <div className="bg-white shadow-sm border-b">
                <div className="container mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <Link to="/" className="text-2xl font-bold text-primary">
                            CopyKiller AI
                        </Link>
                        <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-2">
                                <User className="h-4 w-4 text-gray-500" />
                                <span className="text-sm text-gray-700">{user?.username}</span>
                                {user?.is_premium && (
                                    <Crown className="h-4 w-4 text-yellow-500" />
                                )}
                            </div>
                            <Button variant="outline" size="sm" onClick={handleLogout}>
                                <LogOut className="h-4 w-4 mr-1" />
                                로그아웃
                            </Button>
                        </div>
                    </div>
                </div>
            </div>

            <div className="container mx-auto px-4 py-8">
                {/* 프로필 정보 */}
                <Card className="mb-8">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-3">
                            <User className="h-6 w-6" />
                            내 프로필
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div>
                                <h3 className="font-semibold text-gray-700 mb-2">계정 정보</h3>
                                <p><span className="text-gray-500">사용자명:</span> {user?.username}</p>
                                <p><span className="text-gray-500">이메일:</span> {user?.email}</p>
                                {user?.full_name && (
                                    <p><span className="text-gray-500">이름:</span> {user.full_name}</p>
                                )}
                            </div>
                            <div>
                                <h3 className="font-semibold text-gray-700 mb-2">계정 상태</h3>
                                <div className="flex items-center gap-2 mb-2">
                                    {user?.is_premium ? (
                                        <Badge className="bg-yellow-100 text-yellow-800">
                                            <Crown className="h-3 w-3 mr-1" />
                                            프리미엄
                                        </Badge>
                                    ) : (
                                        <Badge variant="secondary">기본 회원</Badge>
                                    )}
                                </div>
                            </div>
                            <div>
                                <h3 className="font-semibold text-gray-700 mb-2">활동 통계</h3>
                                <p><span className="text-gray-500">총 질문 수:</span> {totalCount}개</p>
                                <p><span className="text-gray-500">오늘 활동:</span> {questions.filter(q => 
                                    new Date(q.created_at).toDateString() === new Date().toDateString()
                                ).length}개</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* 질문 기록 */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-3">
                            <History className="h-6 w-6" />
                            나의 질문 기록
                        </CardTitle>
                        <CardDescription>
                            지금까지의 표절 검사 및 분석 기록을 확인하세요
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        {error && (
                            <Alert className="mb-6 border-red-200 bg-red-50">
                                <AlertDescription className="text-red-600">
                                    {error}
                                </AlertDescription>
                            </Alert>
                        )}

                        {questions.length === 0 ? (
                            <div className="text-center py-12">
                                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                                <h3 className="text-lg font-medium text-gray-900 mb-2">아직 질문 기록이 없습니다</h3>
                                <p className="text-gray-500 mb-6">표절 검사를 시작하여 기록을 남겨보세요.</p>
                                <Button asChild>
                                    <Link to="/">
                                        <Search className="h-4 w-4 mr-2" />
                                        표절 검사 시작하기
                                    </Link>
                                </Button>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {questions.map((question) => (
                                    <Card key={question.id} className="border-l-4 border-l-blue-400">
                                        <CardContent className="p-4">
                                            <div className="flex items-start justify-between">
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-2 mb-2">
                                                        {getQuestionTypeIcon(question.question_type)}
                                                        <Badge variant="outline">
                                                            {getQuestionTypeText(question.question_type)}
                                                        </Badge>
                                                        <Badge variant={question.status === 'completed' ? 'default' : 'secondary'}>
                                                            {question.status === 'completed' ? '완료' : '처리중'}
                                                        </Badge>
                                                        {question.similarity_score !== null && (
                                                            <Badge variant={getSimilarityColor(question.similarity_score)}>
                                                                유사도 {question.similarity_score.toFixed(1)}%
                                                            </Badge>
                                                        )}
                                                    </div>
                                                    
                                                    <p className="text-gray-900 mb-3 line-clamp-2">
                                                        {question.question_text}
                                                    </p>
                                                    
                                                    <div className="flex items-center gap-4 text-sm text-gray-500">
                                                        <div className="flex items-center gap-1">
                                                            <Calendar className="h-4 w-4" />
                                                            {new Date(question.created_at).toLocaleDateString('ko-KR')}
                                                        </div>
                                                        <div className="flex items-center gap-1">
                                                            <Clock className="h-4 w-4" />
                                                            {new Date(question.created_at).toLocaleTimeString('ko-KR')}
                                                        </div>
                                                        {question.match_count > 0 && (
                                                            <div>
                                                                매치 {question.match_count}개
                                                            </div>
                                                        )}
                                                        {question.processing_time && (
                                                            <div>
                                                                처리시간 {question.processing_time.toFixed(2)}초
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                                
                                                <div className="flex items-center space-x-2 ml-4">
                                                    <Button 
                                                        variant="outline" 
                                                        size="sm"
                                                        onClick={() => deleteQuestion(question.id)}
                                                    >
                                                        <Trash2 className="h-4 w-4" />
                                                    </Button>
                                                </div>
                                            </div>
                                        </CardContent>
                                    </Card>
                                ))}
                                
                                {hasMore && (
                                    <div className="text-center pt-4">
                                        <Button variant="outline">
                                            더 보기
                                        </Button>
                                    </div>
                                )}
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* 액션 버튼 */}
                <div className="mt-8 flex justify-center space-x-4">
                    <Button asChild size="lg">
                        <Link to="/">
                            <Search className="h-5 w-5 mr-2" />
                            새 검사 시작하기
                        </Link>
                    </Button>
                    <Button variant="outline" size="lg" asChild>
                        <Link to="/premium">
                            <Crown className="h-5 w-5 mr-2" />
                            프리미엄 기능 보기
                        </Link>
                    </Button>
                </div>
            </div>
        </div>
    );
};

export default MyPage;