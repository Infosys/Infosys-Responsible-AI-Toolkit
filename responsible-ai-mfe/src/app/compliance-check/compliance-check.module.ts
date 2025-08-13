import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../shared/shared.module';
import { ComplianceCheckComponent } from './compliance-check.component';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';

const routes: Routes = [
  { path: '', component: ComplianceCheckComponent }
];

@NgModule({
  declarations: [
    ComplianceCheckComponent
  ],
  imports: [
    CommonModule,
    SharedModule,
    NgxSkeletonLoaderModule,
    RouterModule.forChild(routes)
  ]
})
export class ComplianceCheckModule { }