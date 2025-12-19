import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Eye, EyeOff, User, Mail, Lock, UserPlus, LogIn, CheckCircle, AlertCircle } from 'lucide-react';

interface LoginProps {}

const LoginPage: React.FC<LoginProps> = () => {
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState('login');
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    // 로그인 폼 상태
    const [loginForm, setLoginForm] = useState({
        username_or_email: '',
        password: ''
    });

    // 회원가입 폼 상태
    const [registerForm, setRegisterForm] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        full_name: ''
    });

    // 중복 확인 상태
    const [validation, setValidation] = useState({
        username: { checked: false, available: false, message: '' },
        email: { checked: false, available: false, message: '' }
    });

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await fetch('http://localhost:8006/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(loginForm),
            });

            const data = await response.json();

            if (response.ok) {
                // 토큰과 사용자 정보 저장
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('user_info', JSON.stringify(data.user));
                
                setSuccess('로그인 성공! 메인 페이지로 이동합니다.');
                setTimeout(() => {
                    navigate('/');
                }, 1500);
            } else {
                setError(data.detail || '로그인에 실패했습니다.');
            }
        } catch (error) {
            setError('서버 연결에 실패했습니다. 잠시 후 다시 시도해주세요.');
            console.error('Login error:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        // 비밀번호 확인
        if (registerForm.password !== registerForm.confirmPassword) {
            setError('비밀번호가 일치하지 않습니다.');
            setLoading(false);
            return;
        }

        try {
            const response = await fetch('http://localhost:8006/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: registerForm.username,
                    email: registerForm.email,
                    password: registerForm.password,
                    full_name: registerForm.full_name || null
                }),
            });

            const data = await response.json();

            if (response.ok) {
                setSuccess('회원가입이 완료되었습니다! 로그인 탭으로 이동합니다.');
                setTimeout(() => {
                    setActiveTab('login');
                    setRegisterForm({
                        username: '',
                        email: '',
                        password: '',
                        confirmPassword: '',
                        full_name: ''
                    });
                    setSuccess('');
                }, 2000);
            } else {
                setError(data.detail || '회원가입에 실패했습니다.');
            }
        } catch (error) {
            setError('서버 연결에 실패했습니다. 잠시 후 다시 시도해주세요.');
            console.error('Register error:', error);
        } finally {
            setLoading(false);
        }
    };

    const checkUsername = async (username: string) => {
        if (username.length < 3) {
            setValidation(prev => ({
                ...prev,
                username: { checked: true, available: false, message: '사용자명은 3자 이상이어야 합니다.' }
            }));
            return;
        }

        try {
            const response = await fetch(`http://localhost:8006/api/auth/check-username/${username}`);
            const data = await response.json();

            setValidation(prev => ({
                ...prev,
                username: { 
                    checked: true, 
                    available: data.available, 
                    message: data.message 
                }
            }));
        } catch (error) {
            console.error('Username check error:', error);
        }
    };

    const checkEmail = async (email: string) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            setValidation(prev => ({
                ...prev,
                email: { checked: true, available: false, message: '유효하지 않은 이메일 형식입니다.' }
            }));
            return;
        }

        try {
            const response = await fetch(`http://localhost:8006/api/auth/check-email/${email}`);
            const data = await response.json();

            setValidation(prev => ({
                ...prev,
                email: { 
                    checked: true, 
                    available: data.available, 
                    message: data.message 
                }
            }));
        } catch (error) {
            console.error('Email check error:', error);
        }
    };

    const validatePassword = (password: string) => {
        if (password.length < 8) return '비밀번호는 8자 이상이어야 합니다.';
        if (!/[a-zA-Z]/.test(password)) return '영문자를 포함해야 합니다.';
        if (!/[0-9]/.test(password)) return '숫자를 포함해야 합니다.';
        return '';
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center p-4">
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">CopyKiller AI</h1>
                    <p className="text-gray-600">AI 기반 표절 검사 서비스</p>
                </div>

                <Card className="shadow-lg">
                    <CardHeader>
                        <CardTitle className="text-center">계정 관리</CardTitle>
                        <CardDescription className="text-center">
                            로그인하거나 새 계정을 만드세요
                        </CardDescription>
                    </CardHeader>

                    <CardContent>
                        <Tabs value={activeTab} onValueChange={setActiveTab}>
                            <TabsList className="grid w-full grid-cols-2">
                                <TabsTrigger value="login">로그인</TabsTrigger>
                                <TabsTrigger value="register">회원가입</TabsTrigger>
                            </TabsList>

                            {/* 로그인 탭 */}
                            <TabsContent value="login" className="space-y-4">
                                <form onSubmit={handleLogin} className="space-y-4">
                                    <div className="space-y-2">
                                        <Label htmlFor="login-username">사용자명 또는 이메일</Label>
                                        <div className="relative">
                                            <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                                            <Input
                                                id="login-username"
                                                type="text"
                                                placeholder="사용자명 또는 이메일을 입력하세요"
                                                value={loginForm.username_or_email}
                                                onChange={(e) => setLoginForm(prev => ({
                                                    ...prev,
                                                    username_or_email: e.target.value
                                                }))}
                                                className="pl-10"
                                                required
                                            />
                                        </div>
                                    </div>

                                    <div className="space-y-2">
                                        <Label htmlFor="login-password">비밀번호</Label>
                                        <div className="relative">
                                            <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                                            <Input
                                                id="login-password"
                                                type={showPassword ? "text" : "password"}
                                                placeholder="비밀번호를 입력하세요"
                                                value={loginForm.password}
                                                onChange={(e) => setLoginForm(prev => ({
                                                    ...prev,
                                                    password: e.target.value
                                                }))}
                                                className="pl-10 pr-10"
                                                required
                                            />
                                            <button
                                                type="button"
                                                onClick={() => setShowPassword(!showPassword)}
                                                className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                                            >
                                                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                            </button>
                                        </div>
                                    </div>

                                    {error && (
                                        <Alert className="border-red-200 bg-red-50">
                                            <AlertCircle className="h-4 w-4 text-red-600" />
                                            <AlertDescription className="text-red-600">
                                                {error}
                                            </AlertDescription>
                                        </Alert>
                                    )}

                                    {success && (
                                        <Alert className="border-green-200 bg-green-50">
                                            <CheckCircle className="h-4 w-4 text-green-600" />
                                            <AlertDescription className="text-green-600">
                                                {success}
                                            </AlertDescription>
                                        </Alert>
                                    )}

                                    <Button 
                                        type="submit" 
                                        className="w-full" 
                                        disabled={loading}
                                    >
                                        {loading ? (
                                            <>
                                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                                로그인 중...
                                            </>
                                        ) : (
                                            <>
                                                <LogIn className="h-4 w-4 mr-2" />
                                                로그인
                                            </>
                                        )}
                                    </Button>
                                </form>
                            </TabsContent>

                            {/* 회원가입 탭 */}
                            <TabsContent value="register" className="space-y-4">
                                <form onSubmit={handleRegister} className="space-y-4">
                                    <div className="space-y-2">
                                        <Label htmlFor="register-username">사용자명</Label>
                                        <div className="relative">
                                            <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                                            <Input
                                                id="register-username"
                                                type="text"
                                                placeholder="사용자명 (3자 이상)"
                                                value={registerForm.username}
                                                onChange={(e) => {
                                                    setRegisterForm(prev => ({
                                                        ...prev,
                                                        username: e.target.value
                                                    }));
                                                    if (e.target.value.length >= 3) {
                                                        checkUsername(e.target.value);
                                                    }
                                                }}
                                                className="pl-10"
                                                required
                                            />
                                        </div>
                                        {validation.username.checked && (
                                            <p className={`text-sm ${validation.username.available ? 'text-green-600' : 'text-red-600'}`}>
                                                {validation.username.message}
                                            </p>
                                        )}
                                    </div>

                                    <div className="space-y-2">
                                        <Label htmlFor="register-email">이메일</Label>
                                        <div className="relative">
                                            <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                                            <Input
                                                id="register-email"
                                                type="email"
                                                placeholder="이메일을 입력하세요"
                                                value={registerForm.email}
                                                onChange={(e) => {
                                                    setRegisterForm(prev => ({
                                                        ...prev,
                                                        email: e.target.value
                                                    }));
                                                    if (e.target.value.includes('@')) {
                                                        checkEmail(e.target.value);
                                                    }
                                                }}
                                                className="pl-10"
                                                required
                                            />
                                        </div>
                                        {validation.email.checked && (
                                            <p className={`text-sm ${validation.email.available ? 'text-green-600' : 'text-red-600'}`}>
                                                {validation.email.message}
                                            </p>
                                        )}
                                    </div>

                                    <div className="space-y-2">
                                        <Label htmlFor="register-fullname">이름 (선택사항)</Label>
                                        <Input
                                            id="register-fullname"
                                            type="text"
                                            placeholder="실명을 입력하세요"
                                            value={registerForm.full_name}
                                            onChange={(e) => setRegisterForm(prev => ({
                                                ...prev,
                                                full_name: e.target.value
                                            }))}
                                        />
                                    </div>

                                    <div className="space-y-2">
                                        <Label htmlFor="register-password">비밀번호</Label>
                                        <div className="relative">
                                            <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                                            <Input
                                                id="register-password"
                                                type={showPassword ? "text" : "password"}
                                                placeholder="비밀번호 (8자 이상, 영문+숫자)"
                                                value={registerForm.password}
                                                onChange={(e) => setRegisterForm(prev => ({
                                                    ...prev,
                                                    password: e.target.value
                                                }))}
                                                className="pl-10 pr-10"
                                                required
                                            />
                                            <button
                                                type="button"
                                                onClick={() => setShowPassword(!showPassword)}
                                                className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                                            >
                                                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                            </button>
                                        </div>
                                        {registerForm.password && (
                                            <p className="text-sm text-red-600">
                                                {validatePassword(registerForm.password)}
                                            </p>
                                        )}
                                    </div>

                                    <div className="space-y-2">
                                        <Label htmlFor="register-confirm-password">비밀번호 확인</Label>
                                        <div className="relative">
                                            <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                                            <Input
                                                id="register-confirm-password"
                                                type={showConfirmPassword ? "text" : "password"}
                                                placeholder="비밀번호를 다시 입력하세요"
                                                value={registerForm.confirmPassword}
                                                onChange={(e) => setRegisterForm(prev => ({
                                                    ...prev,
                                                    confirmPassword: e.target.value
                                                }))}
                                                className="pl-10 pr-10"
                                                required
                                            />
                                            <button
                                                type="button"
                                                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                                className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                                            >
                                                {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                            </button>
                                        </div>
                                        {registerForm.confirmPassword && registerForm.password !== registerForm.confirmPassword && (
                                            <p className="text-sm text-red-600">
                                                비밀번호가 일치하지 않습니다.
                                            </p>
                                        )}
                                    </div>

                                    {error && (
                                        <Alert className="border-red-200 bg-red-50">
                                            <AlertCircle className="h-4 w-4 text-red-600" />
                                            <AlertDescription className="text-red-600">
                                                {error}
                                            </AlertDescription>
                                        </Alert>
                                    )}

                                    {success && (
                                        <Alert className="border-green-200 bg-green-50">
                                            <CheckCircle className="h-4 w-4 text-green-600" />
                                            <AlertDescription className="text-green-600">
                                                {success}
                                            </AlertDescription>
                                        </Alert>
                                    )}

                                    <Button 
                                        type="submit" 
                                        className="w-full" 
                                        disabled={loading || !validation.username.available || !validation.email.available}
                                    >
                                        {loading ? (
                                            <>
                                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                                가입 중...
                                            </>
                                        ) : (
                                            <>
                                                <UserPlus className="h-4 w-4 mr-2" />
                                                회원가입
                                            </>
                                        )}
                                    </Button>
                                </form>
                            </TabsContent>
                        </Tabs>

                        <div className="mt-6 text-center">
                            <Button variant="outline" asChild>
                                <Link to="/">
                                    홈으로 돌아가기
                                </Link>
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default LoginPage;