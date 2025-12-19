import React from 'react';
import AICrawlingManager from '@/components/AICrawlingManager';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const AICrawlingPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 상단 네비게이션 */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Button
              variant="ghost"
              onClick={() => navigate('/')}
              className="flex items-center space-x-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>메인으로 돌아가기</span>
            </Button>
            
            <div className="text-sm text-gray-500">
              관리자 전용 • AI 크롤링 관리
            </div>
          </div>
        </div>
      </div>

      {/* 메인 콘텐츠 */}
      <div className="py-8">
        <AICrawlingManager />
      </div>
    </div>
  );
};

export default AICrawlingPage;