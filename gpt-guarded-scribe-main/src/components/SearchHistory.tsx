import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Search, History, Download, Trash2 } from 'lucide-react';
import { CheckResult } from './PlagiarismChecker';
import { cn } from '@/lib/utils';

interface SearchHistoryProps {
  results: CheckResult[];
}

export const SearchHistory: React.FC<SearchHistoryProps> = ({ results }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'date' | 'similarity'>('date');

  const filteredResults = results.filter(result => 
    result.originalText.toLowerCase().includes(searchQuery.toLowerCase()) ||
    result.matches.some(match => 
      match.source.toLowerCase().includes(searchQuery.toLowerCase())
    )
  );

  const sortedResults = [...filteredResults].sort((a, b) => {
    if (sortBy === 'date') {
      return b.timestamp.getTime() - a.timestamp.getTime();
    }
    return b.similarity - a.similarity;
  });

  const getSimilarityColor = (similarity: number) => {
    if (similarity < 15) return 'success';
    if (similarity < 40) return 'warning';
    return 'destructive';
  };

  const getSimilarityLabel = (similarity: number) => {
    if (similarity < 15) return '안전';
    if (similarity < 40) return '주의';
    return '위험';
  };

  if (results.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <History className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">검사 기록이 없습니다</h3>
          <p className="text-muted-foreground">
            완료된 검사 결과가 여기에 표시됩니다.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <History className="h-5 w-5" />
          <span>검사 기록</span>
          <Badge variant="secondary">{results.length}</Badge>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Search and Filter */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="검사 기록 검색..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <div className="flex space-x-2">
            <Button
              variant={sortBy === 'date' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSortBy('date')}
            >
              날짜순
            </Button>
            <Button
              variant={sortBy === 'similarity' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSortBy('similarity')}
            >
              유사도순
            </Button>
          </div>
        </div>

        {/* Results List */}
        <div className="space-y-3">
          {sortedResults.map((result) => (
            <Card key={result.id} className="p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <Badge variant="outline" className="text-xs">
                      #{result.id}
                    </Badge>
                    <Badge 
                      variant={
                        getSimilarityColor(result.similarity) === 'success' ? 'default' :
                        getSimilarityColor(result.similarity) === 'warning' ? 'secondary' : 'destructive'
                      }
                      className="text-xs"
                    >
                      {result.similarity.toFixed(1)}% - {getSimilarityLabel(result.similarity)}
                    </Badge>
                  </div>
                  
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {result.originalText.substring(0, 150)}
                    {result.originalText.length > 150 && '...'}
                  </p>
                  
                  <div className="flex items-center space-x-4 mt-2 text-xs text-muted-foreground">
                    <span>{result.timestamp.toLocaleDateString()}</span>
                    <span>{result.matches.length}개 일치 발견</span>
                    <span>{Math.ceil(result.originalText.length / 500)}분 소요</span>
                  </div>
                </div>

                <div className="flex items-center space-x-1 ml-4">
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                    <Download className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-destructive hover:text-destructive">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Match Sources Preview */}
              {result.matches.length > 0 && (
                <div className="pt-3 border-t">
                  <p className="text-xs font-medium mb-2">주요 출처:</p>
                  <div className="flex flex-wrap gap-1">
                    {result.matches.slice(0, 3).map((match, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {match.source.length > 30 ? match.source.substring(0, 30) + '...' : match.source}
                      </Badge>
                    ))}
                    {result.matches.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{result.matches.length - 3}개 더
                      </Badge>
                    )}
                  </div>
                </div>
              )}
            </Card>
          ))}
        </div>

        {filteredResults.length === 0 && searchQuery && (
          <div className="text-center py-8">
            <Search className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
            <p className="text-sm text-muted-foreground">
              "{searchQuery}"에 대한 검색 결과가 없습니다.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};