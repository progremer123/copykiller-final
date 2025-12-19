import React from 'react';
import { PremiumFeatures } from '@/components/PremiumFeatures';

const Premium: React.FC = () => {
    return (
        <div className="min-h-screen bg-gray-50">
            {/* Navigation Header */}
            <header className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <div className="flex items-center">
                            <h1 className="text-xl font-bold text-gray-900">
                                🔍 CopyKiller Premium
                            </h1>
                        </div>
                        <nav className="flex space-x-4">
                            <a href="/" className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">
                                홈
                            </a>
                            <a href="#" className="bg-purple-600 text-white px-3 py-2 rounded-md text-sm font-medium">
                                프리미엄
                            </a>
                        </nav>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <PremiumFeatures />
            </main>
        </div>
    );
};

export default Premium;