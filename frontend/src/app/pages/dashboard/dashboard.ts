// src/app/pages/dashboard/dashboard.component.ts

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MarkdownModule } from 'ngx-markdown';
import { AuthService } from '../../services/auth';
import { StockService } from '../../services/stock.service';
import { UserResponse } from '../../models/user.models';
import { Stock, MarketSummary, AICorrelation, TrendAnalysis, AIPrediction } from '../../models/stock.models';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule, MarkdownModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class DashboardComponent implements OnInit {
  currentUser: UserResponse | null = null;
  isLoading = false;
  
  // 🆕 CAMBIAR VISTAS: overview, stocks, analysis, video
  activeView: 'overview' | 'stocks' | 'analysis' | 'video' = 'overview';
  
  selectedTicker = '';
  availableTickers = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'VS', 'MA'];
  
  // Para Overview
  selectedTickersForOverview: string[] = [];
  selectedStock: Stock | null = null;
  marketSummary: MarketSummary | null = null;
  trendAnalysis: TrendAnalysis | null = null;
  
  // Para Analysis (AI Correlation + Prediction)
  aiCorrelation: AICorrelation | null = null;
  aiPrediction: AIPrediction | null = null;
  
  // Para Video Generator
  isGeneratingVideo = false;
  videoUrl: string | null = null;
  videoFilename: string | null = null;
  
  errorMessage = '';
  successMessage = '';

  constructor(
    private authService: AuthService,
    private stockService: StockService,
    private router: Router
  ) {}

  ngOnInit(): void {
    console.log('🔵 Dashboard initialized');
    
    this.currentUser = this.authService.getCurrentUser();
    
    if (this.currentUser?.id) {
      this.loadUserData(this.currentUser.id);
    }
  }

  loadUserData(userId: string): void {
    this.isLoading = true;
    this.authService.getUserById(userId).subscribe({
      next: (user: UserResponse) => {
        this.currentUser = user;
        this.isLoading = false;
      },
      error: (error: any) => {
        console.error('❌ Failed to load user data:', error);
        this.isLoading = false;
      }
    });
  }

  switchView(view: 'overview' | 'stocks' | 'analysis' | 'video'): void {
    this.activeView = view;
    this.clearMessages();
    
    // Limpiar datos al cambiar de vista
    if (view !== 'overview') {
      this.marketSummary = null;
      this.trendAnalysis = null;
    }
    if (view !== 'analysis') {
      this.aiCorrelation = null;
      this.aiPrediction = null;
    }
    if (view !== 'video') {
      this.videoUrl = null;
      this.videoFilename = null;
    }
  }

  // ====================================
  // OVERVIEW: Selección de tickers
  // ====================================
  
  toggleTickerSelection(ticker: string): void {
    const index = this.selectedTickersForOverview.indexOf(ticker);
    
    if (index > -1) {
      this.selectedTickersForOverview.splice(index, 1);
    } else {
      this.selectedTickersForOverview.push(ticker);
    }
    
    if (this.selectedTickersForOverview.length > 0) {
      this.loadMarketSummary();
      this.loadTrendAnalysisForSelected();
    } else {
      this.marketSummary = null;
      this.trendAnalysis = null;
    }
  }

  isTickerSelected(ticker: string): boolean {
    return this.selectedTickersForOverview.includes(ticker);
  }

  loadMarketSummary(): void {
    if (this.selectedTickersForOverview.length === 0) {
      this.errorMessage = 'Please select at least one ticker';
      return;
    }

    this.isLoading = true;
    this.clearMessages();
    
    console.log('🔵 Loading market summary for:', this.selectedTickersForOverview);
    
    this.stockService.getMarketSummary(this.selectedTickersForOverview).subscribe({
      next: (summary: MarketSummary) => {
        console.log('✅ Market summary loaded:', summary);
        this.marketSummary = summary;
        this.isLoading = false;
      },
      error: (error: any) => {
        console.error('❌ Failed to load market summary:', error);
        this.errorMessage = 'Failed to load market data';
        this.isLoading = false;
      }
    });
  }

  // 🆕 TREND ANALYSIS EN OVERVIEW
  loadTrendAnalysisForSelected(): void {
    if (this.selectedTickersForOverview.length === 0) return;
    
    this.stockService.getTrendAnalysis(this.selectedTickersForOverview).subscribe({
      next: (trends: TrendAnalysis) => {
        console.log('✅ Trend analysis loaded:', trends);
        this.trendAnalysis = trends;
      },
      error: (error: any) => {
        console.error('❌ Failed to load trend analysis:', error);
      }
    });
  }

  // ====================================
  // STOCKS: Búsqueda individual
  // ====================================
  
  searchStock(): void {
    if (!this.selectedTicker) {
      this.errorMessage = 'Please enter a ticker symbol';
      return;
    }

    this.isLoading = true;
    this.clearMessages();
    
    this.stockService.runETL(this.selectedTicker.toUpperCase()).subscribe({
      next: (response: any) => {
        console.log('✅ ETL executed:', response);
        this.selectedStock = response.data;
        this.successMessage = `Data updated for ${this.selectedTicker}`;
        this.isLoading = false;
      },
      error: (error: any) => {
        console.error('❌ Failed to search stock:', error);
        this.errorMessage = `Failed to fetch data for ${this.selectedTicker}`;
        this.isLoading = false;
      }
    });
  }

  // ====================================
  // ANALYSIS: AI Correlation + Prediction
  // ====================================
  
  loadAICorrelation(): void {
    if (!this.selectedTicker) {
      this.errorMessage = 'Please enter a ticker symbol';
      return;
    }

    this.isLoading = true;
    this.clearMessages();
    this.aiPrediction = null; // Limpiar prediction
    
    this.stockService.getAICorrelation(this.selectedTicker.toUpperCase()).subscribe({
      next: (correlation: AICorrelation) => {
        this.aiCorrelation = correlation;
        this.isLoading = false;
      },
      error: (error: any) => {
        console.error('❌ Failed to load AI correlation:', error);
        this.errorMessage = 'Failed to load AI analysis';
        this.isLoading = false;
      }
    });
  }

  loadAIPrediction(): void {
    if (!this.selectedTicker) {
      this.errorMessage = 'Please enter a ticker symbol';
      return;
    }

    this.isLoading = true;
    this.clearMessages();
    this.aiCorrelation = null; // Limpiar correlation
    
    this.stockService.getAIPrediction(this.selectedTicker.toUpperCase()).subscribe({
      next: (prediction: AIPrediction) => {
        this.aiPrediction = prediction;
        this.isLoading = false;
      },
      error: (error: any) => {
        console.error('❌ Failed to load AI prediction:', error);
        this.errorMessage = 'Failed to load prediction';
        this.isLoading = false;
      }
    });
  }

  // ====================================
  // VIDEO GENERATOR
  // ====================================
  
  generateVideo(): void {
    if (!this.selectedTicker) {
      this.errorMessage = 'Please enter a ticker symbol first';
      return;
    }

    this.isGeneratingVideo = true;
    this.clearMessages();
    this.videoUrl = null;
    this.videoFilename = null;
    
    console.log('🎬 Generating video for:', this.selectedTicker);

    this.stockService.generateVideo(this.selectedTicker.toUpperCase()).subscribe({
      next: (videoBlob: Blob) => {
        console.log('✅ Video generated successfully');
        
        // Crear URL local para el blob
        this.videoUrl = URL.createObjectURL(videoBlob);
        
        // Guardar nombre del archivo para descarga
        const date = new Date().toISOString().split('T')[0];
        this.videoFilename = `stock-video-${this.selectedTicker}-${date}.mp4`;
        
        this.successMessage = `Video generated for ${this.selectedTicker}!`;
        this.isGeneratingVideo = false;
      },
      error: (error: any) => {
        console.error('❌ Failed to generate video:', error);
        this.errorMessage = 'Failed to generate video. This process can take several minutes. Please try again.';
        this.isGeneratingVideo = false;
      }
    });
  }

  downloadVideo(): void {
    if (!this.videoUrl || !this.videoFilename) return;
    
    const link = document.createElement('a');
    link.href = this.videoUrl;
    link.download = this.videoFilename;
    link.click();
  }

  clearMessages(): void {
    this.errorMessage = '';
    this.successMessage = '';
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  getChangeColor(change: number): string {
    return change > 0 ? '#4caf50' : change < 0 ? '#f44336' : '#999';
  }

  formatChange(change: number): string {
    return change > 0 ? `+${change.toFixed(2)}%` : `${change.toFixed(2)}%`;
  }
}