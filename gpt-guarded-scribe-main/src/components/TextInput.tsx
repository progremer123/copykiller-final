import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { FileText, Search } from 'lucide-react';

interface TextInputProps {
  onTextSubmit: (text: string) => void;
}

export const TextInput: React.FC<TextInputProps> = ({ onTextSubmit }) => {
  const [text, setText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const wordCount = text.trim().split(/\s+/).filter(word => word.length > 0).length;
  const charCount = text.length;

  const handleSubmit = async () => {
    if (!text.trim()) {
      alert('검사할 텍스트를 입력해주세요.');
      return;
    }

    if (wordCount < 10) {
      alert('최소 10단어 이상 입력해주세요.');
      return;
    }

    setIsSubmitting(true);
    
    try {
      await onTextSubmit(text);
      setText('');
    } catch (error) {
      console.error('Submission failed:', error);
      alert('텍스트 제출에 실패했습니다. 다시 시도해주세요.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getSampleText = () => {
    const samples = [
      "인공지능은 현대 사회의 여러 분야에서 혁신적인 변화를 이끌고 있습니다. 특히 의료, 교육, 금융 등의 영역에서 AI 기술의 활용이 급속도로 확산되고 있으며, 이는 인간의 삶의 질 향상에 크게 기여하고 있습니다.",
      "기후 변화는 21세기 인류가 직면한 가장 심각한 도전 중 하나입니다. 지구 온난화로 인한 해수면 상승, 극단적 기상 현상의 증가, 생태계 파괴 등은 전 세계적인 대응을 필요로 합니다.",
      "디지털 트랜스포메이션은 기업의 생존과 성장을 위한 필수 요소가 되었습니다. 클라우드 컴퓨팅, 빅데이터, IoT 기술의 융합을 통해 새로운 비즈니스 모델과 고객 경험이 창출되고 있습니다."
    ];
    
    const randomSample = samples[Math.floor(Math.random() * samples.length)];
    setText(randomSample);
  };

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <FileText className="h-5 w-5 text-primary" />
            <h3 className="text-lg font-semibold">텍스트 입력</h3>
          </div>
          <Button variant="outline" size="sm" onClick={getSampleText}>
            샘플 텍스트
          </Button>
        </div>

        <Textarea
          placeholder="검사할 텍스트를 입력하세요. 최소 10단어 이상 입력해주세요."
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="min-h-[500px] text-base leading-relaxed"
          disabled={isSubmitting}
        />

        <div className="flex items-center justify-between">
          <div className="flex space-x-4">
            <Badge variant="secondary">
              {wordCount} 단어
            </Badge>
            <Badge variant="secondary">
              {charCount} 글자
            </Badge>
          </div>

          <div className="text-sm text-muted-foreground">
            {wordCount < 10 && text.length > 0 && (
              <span className="text-warning">최소 10단어가 필요합니다</span>
            )}
          </div>
        </div>
      </div>

      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Search className="h-5 w-5 text-primary" />
              <h4 className="font-medium">검사 정보</h4>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="space-y-1">
                <p className="font-medium text-foreground">검사 범위</p>
                <p className="text-muted-foreground">학술 논문, 웹 문서, 뉴스 기사</p>
              </div>
              <div className="space-y-1">
                <p className="font-medium text-foreground">검사 방식</p>
                <p className="text-muted-foreground">AI 기반 의미론적 분석</p>
              </div>
              <div className="space-y-1">
                <p className="font-medium text-foreground">예상 시간</p>
                <p className="text-muted-foreground">2-5분 (텍스트 길이에 따라)</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Button 
        onClick={handleSubmit}
        disabled={!text.trim() || wordCount < 10 || isSubmitting}
        className="w-full"
        size="lg"
      >
        {isSubmitting ? (
          <>
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            표절 검사 중...
          </>
        ) : (
          <>
            <Search className="h-4 w-4 mr-2" />
            표절 검사 시작
          </>
        )}
      </Button>
    </div>
  );
};