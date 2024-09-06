import { Component, OnInit } from '@angular/core';
import { WebhookService } from '../webhook.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-webhook-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './webhook-list.component.html',
  styleUrls: ['./webhook-list.component.scss']
})
export class WebhookListComponent implements OnInit {
  requests: any[] = [];
  intervalId: any;
  lastUpdated: Date | null = null;

  constructor(private webhookService: WebhookService) { }

  ngOnInit(): void {
    this.fetchRequests();
    this.intervalId = setInterval(() => this.fetchRequests(), 15000); // Fetch every 15 seconds
  }

  ngOnDestroy(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
  }

  fetchRequests(): void {
    this.webhookService.getRequests().subscribe(data => {
      this.requests = data;
      console.log(data);
      this.lastUpdated = new Date();
    });
  }
}
